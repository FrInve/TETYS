import logging
import os

# Remove this comment to set the cache directory in another location
# os.environ['HF_HOME'] = '/data/hf_cache'
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModel
from bertopic.backend import BaseEmbedder
from transformers.pipelines import pipeline

### CONFIGURATION ###
DATASET_PATH = "./data/processed/metadata_clean.parquet"
DATASET_TEXT_FEATURE = (
    "abstract"  # In the dataset file, the column name that contains the text data
)
TASK_FOR_LLM = "Cluster this research title and abstract: "
OUTPUT_PATH = "./data/interim/embeddings.npy"

### END OF CONFIGURATION ###

# Set logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s:%(message)s",
    filename="./logs/2-optimization-1_embeddings.log",
    encoding="utf-8",
    level=logging.INFO,
)
logging.getLogger().addHandler(logging.StreamHandler())

# Log starting message
logging.info("############ Starting... ############")

# Check if CUDA is available
logging.info(f"CUDA is available? {torch.cuda.is_available()}")

# Set number of threads in torch to leave some CPU to other users
torch.set_num_threads(8)


# Data structure to load the data into a GPU
class ListDataset(Dataset):
    def __init__(self, original_list):
        self.original_list = original_list

    def __len__(self):
        return len(self.original_list)

    def __getitem__(self, i):
        return self.original_list[i]


# Function to get the last token of a sequence
# Used to get the embeddings of the last token of a sequence,
# which is the token that represents the whole sequence
def last_token_pool(
    last_hidden_states: torch.Tensor, attention_mask: torch.Tensor
) -> torch.Tensor:
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[
            torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths
        ]


# Create custom backend
# Set the model and tokenizer to use - from Hugging Face
tokenizer = "Salesforce/SFR-Embedding-2_R"
embedding_model = "Salesforce/SFR-Embedding-2_R"
model = "Salesforce-SFR-Embedding-2_R"

# Use a pre-defined transformer pipeline "feature-extraction" to
# transform a given document into the embeddings
tokenizer = AutoTokenizer.from_pretrained(tokenizer)
embedding_model = pipeline(
    task="feature-extraction", model=embedding_model, tokenizer=tokenizer, device="cuda"
)
print("Model loaded")

# Load here the data in parquet format
df = pd.read_parquet(DATASET_PATH)
logging.info("Data loaded")
logging.info(f"Number of documents: {df.shape[0]}")


df["passages"] = df[DATASET_TEXT_FEATURE].apply(lambda x: TASK_FOR_LLM + x)
passages = ListDataset(df.passages.to_list())

logging.info("Model and data are ready...")
logging.info("Computing embeddings. Please wait.")

embeddings = []
print("___________")

# Create the file path to store the embeddings
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


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

logging.info(f"Embeddings computed. Saving to {OUTPUT_PATH}")
with open(OUTPUT_PATH, "wb") as f:
    np.save(f, embeddings, allow_pickle=False)

logging.info(f"########### END :D ###########")

# Old code
# Deprecated
"""
# Load data
df = pd.read_parquet("./data/processed/metadata_clean.parquet")
abstracts = df.abstract.to_list()
logging.info("Data loaded")

# Load model
embedding_model = SentenceTransformer(
    "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
)
logging.info("Model is ready...")

# Compute embeddings
logging.info("Computing embeddings. Please wait.")
embeddings = embedding_model.encode(abstracts, show_progress_bar=False)

logging.info("Finished! Storing embeddings to data/interim/embeddings.npy")

with open("./data/interim/embeddings.npy", "wb") as f:
    np.save(f, embeddings)
"""
