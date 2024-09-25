import logging
import os
os.environ['HF_HOME'] = '/data/hf_cache'
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModel
from bertopic.backend import BaseEmbedder
from transformers.pipelines import pipeline

GROUP=4
print(torch.cuda.is_available())

class ListDataset(Dataset):
    def __init__(self, original_list):
        self.original_list = original_list

    def __len__(self):
        return len(self.original_list)

    def __getitem__(self, i):
        return self.original_list[i]

def last_token_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


# Create custom backend
tokenizer = 'Salesforce/SFR-Embedding-2_R'
embedding_model = 'Salesforce/SFR-Embedding-2_R'
model = 'Salesforce-SFR-Embedding-2_R'

#pipeline
tokenizer = AutoTokenizer.from_pretrained(tokenizer)
embedding_model = pipeline(task="feature-extraction", model=embedding_model, tokenizer=tokenizer,device="cuda")
print("Model loaded")

logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f'./logs/group_{GROUP}/embeddings_LLM_group_{GROUP}_{model}.log', encoding='utf-8', level=logging.INFO)
logging.info("Starting...")
df = pd.read_parquet(f'./data/processed/group_{GROUP}/metadata_clean_group_{GROUP}.parquet')
print(len(df))
logging.info("Data loaded")
logging.info(f"Number of abstracts: {df.shape[0]}")

task = "Cluster this research title and abstract: "
df["passages"] = df.abstract.apply(lambda x: task + x)
passages = ListDataset(df.passages.to_list())

logging.info("Model is ready...")
logging.info("Computing embeddings. Please wait.")

embeddings = []
print("___________")

file_path = f'./data/interim/group_{GROUP}/embeddings_{model}_LLM_group_{GROUP}.npy'

if not os.path.exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

for text in tqdm(passages, total=len(passages)):
    inputs = tokenizer(text, return_tensors="pt", padding=True).to("cuda")
    with torch.no_grad():
        outputs = embedding_model.model(**inputs)
    last_hidden_states = outputs.last_hidden_state
    attention_mask = inputs.attention_mask
    last_token_embedding = last_token_pool(last_hidden_states, attention_mask)
    embeddings.append(last_token_embedding.cpu())

embeddings = [tensor.numpy() for tensor in embeddings]
embeddings = [embedding[0] for embedding in embeddings]
embeddings = np.array(embeddings)
print("DONE\n__________")

logging.info(f"Embeddings computed. Saving...")
with open(file_path,'wb') as f:
    np.save(f, embeddings, allow_pickle=False)

logging.info(f"Finished! Storing embeddings to {file_path}")
