import logging

import numpy as np
import pandas as pd
import torch
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from bertopic.vectorizers import ClassTfidfTransformer
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP


def create_model():
    # Step 1 - Extract embeddings
    embedding_model = SentenceTransformer("sentence-transformers/allenai-specter")

    # Step 2 - Reduce dimensionality
    umap_model = UMAP(n_neighbors=15, n_components=30, min_dist=0.0, metric='cosine')

    # Step 3 - Cluster reduced embeddings
    hdbscan_model = HDBSCAN(min_cluster_size=25, min_samples=10, metric='euclidean', cluster_selection_method='eom', prediction_data=True)

    # Step 4 - Tokenize topics
    vectorizer_model = CountVectorizer(stop_words="english", token_pattern="(?u)\\b[\\w-]+\\b")

    # Step 5 - Create topic representation
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

    # Step 6 - (Optional) Fine-tune topic representations with 
    # a `bertopic.representation` model
    representation_model = KeyBERTInspired()

    # All steps together
    topic_model = BERTopic(
    embedding_model=embedding_model,          # Step 1 - Extract embeddings
    umap_model=umap_model,                    # Step 2 - Reduce dimensionality
    hdbscan_model=hdbscan_model,              # Step 3 - Cluster reduced embeddings
    vectorizer_model=vectorizer_model,        # Step 4 - Tokenize topics
    ctfidf_model=ctfidf_model,                # Step 5 - Extract topic words
    representation_model=representation_model, # Step 6 - (Optional) Fine-tune topic represenations
    verbose=True
    )
    
    return topic_model

if __name__ == '__main__':
    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/bertopic.log', encoding='utf-8', level=logging.INFO)

    logging.info("Starting...")
    np.random.seed(777)
    torch.set_num_threads(28)

    # Load data
    df = pd.read_csv('./data/raw/nature/climate_change.csv')
    df = df[df.language == "en"]
    df = df[df.abstract.notna()]
    abstracts = df.abstract.to_list()
    abstracts = [str(x) for x in abstracts]
    logging.info(f"Data loaded - {len(abstracts)} abstracts available")

    # Create model
    topic_model = create_model()
    logging.info("BERTopic model created")

    logging.info("Fitting the model and transforming data...")
    topics, probs = topic_model.fit_transform(abstracts)

    logging.info("BERTopic model fitted and data transformed.")

    topic_model.save('./models/BERTopic_full_climate_2023-07-13', save_embedding_model=False)
    logging.info("Model saved in ./models")

