import logging

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

# Set logging
logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/embeddings.log', encoding='utf-8', level=logging.INFO)

# Set number of threads in torch to leave some CPU to other users
logging.info("Starting...")
torch.set_num_threads(28)

# Load data
df = pd.read_csv('./data/raw/nature/climate_change.csv')
df = df[df.language == "en"]
df = df[df.abstract.notna()]
df_sample = df.sample(frac=0.5)
abstracts = df_sample.abstract.to_list()
abstracts = [str(x) for x in abstracts]

logging.info(f"Data loaded - {len(abstracts)} abstracts available")

# Load model
embedding_model = SentenceTransformer("sentence-transformers/allenai-specter")
logging.info("Model is ready...")

# Compute embeddings
logging.info("Computing embeddings. Please wait.")
embeddings = embedding_model.encode(abstracts, show_progress_bar=False)

logging.info("Finished! Storing embeddings to data/interim/embeddings_specter_climate.npy")

with open('./data/interim/embeddings_specter_climate.npy','wb') as f:
    np.save(f, embeddings)
