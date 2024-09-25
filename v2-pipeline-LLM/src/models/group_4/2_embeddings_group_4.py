import logging
import os
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

GROUP=4
model = "sentence_transformers_allenai_specter"

# Set logging
logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f'./logs/group_{GROUP}/embeddings_group_{GROUP}_{model}.log', encoding='utf-8', level=logging.INFO)

# Set number of threads in torch to leave some CPU to other users
logging.info("Starting...")
torch.set_num_threads(28)

# Load data
df = pd.read_parquet(f'./data/processed/group_{GROUP}/metadata_clean_group_{GROUP}.parquet')
abstracts = df.abstract.to_list()
logging.info("Data loaded")
logging.info(f"Number of abstracts: {len(abstracts)}")
print(df.head())

# Load model
embedding_model = SentenceTransformer('sentence-transformers/allenai-specter')

logging.info("Model is ready...")

# Compute embeddings
logging.info("Computing embeddings. Please wait.")
embeddings = embedding_model.encode(abstracts, show_progress_bar=True)

file_path = f'./data/interim/group_{GROUP}/embeddings_{model}_group_{GROUP}.npy'

if not os.path.exists(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
with open(file_path,'wb') as f:
    np.save(f, embeddings)

logging.info(f"Finished! Storing embeddings to {file_path}")
