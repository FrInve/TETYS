import logging

import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

# Set logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s:%(message)s",
    filename="./logs/embeddings.log",
    encoding="utf-8",
    level=logging.INFO,
)
logging.getLogger().addHandler(logging.StreamHandler())

# Set number of threads in torch to leave some CPU to other users
logging.info("Starting...")
torch.set_num_threads(8)

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
