import logging
import os

# Remove this comment to set the cache directory in another location
# os.environ['HF_HOME'] = '/data/hf_cache'
import pandas as pd
import numpy as np
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from umap import UMAP
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
import torch
from torch.utils.data import Dataset
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModel
from bertopic.backend import BaseEmbedder
from transformers.pipelines import pipeline
from sklearn.model_selection import ParameterSampler
from spacy.lang.it.stop_words import STOP_WORDS

### CONFIGURATION ###
DATASET_PATH = "./data/processed/metadata_clean_laws.parquet"
DATASET_AS_EMBEDDINGS_PATH = "./data/interim/embeddings.npy"
BEST_MODELS_PATH = "./models/tuning/"
DATASET_TEXT_FEATURE = (
    "Title"  # In the dataset file, the column name that contains the text data
)
TASK_FOR_LLM = "Cluster this laws' titles'"
VALIDATION_SPLIT_PERCENTAGE = 0.25
NUMBER_OF_ITERATIONS = 100
#NUMBER_OF_ITERATIONS = 300
TOKENIZER = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

### END OF CONFIGURATION ###


def create_model(umap_model_, hdbscan_model_):
    """
    Create a BERTopic model with the initialized UMAP and HDBSCAN models
    """
    vectorizer_model = CountVectorizer(
        stop_words=list(STOP_WORDS), token_pattern="(?u)\\b[\\w-]+\\b"
    )
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    representation_model = KeyBERTInspired()

    # Use a predefined pytorch pipeline for feature extraction to compute embeddings
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
    embedding_model = pipeline(
        task="feature-extraction",
        model=EMBEDDING_MODEL,
        tokenizer=tokenizer,
        device="cpu",
    )

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model_,  # Step 2 - Reduce dimensionality
        hdbscan_model=hdbscan_model_,  # Step 3 - Cluster reduced embeddings
        vectorizer_model=vectorizer_model,  # Step 4 - Tokenize topics
        ctfidf_model=ctfidf_model,  # Step 5 - Extract topic words
        representation_model=representation_model,  # Step 6 - (Optional) Fine-tune topic represenations
        verbose=True,
    )

    return topic_model


if __name__ == "__main__":
    # Set logging
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s:%(message)s",
        filename=f"./logs/tuning.log",
        encoding="utf-8",
        level=logging.INFO,
    )

    logging.info("############## Starting... ##############")
    np.random.seed(777)

    df = pd.read_parquet(DATASET_PATH)
    # apply str to all elements in documents to avoid TypeError: expected string or bytes-like object
    documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()
    logging.info(f"Data loaded - {len(documents)} documents available")

    with open(DATASET_AS_EMBEDDINGS_PATH, "rb") as f:
        embeddings = np.load(f)
    logging.info("Data loaded")

    # generate random boolean mask the length of data
    mask = np.random.choice(
        [False, True],
        len(embeddings),
        p=[1 - VALIDATION_SPLIT_PERCENTAGE, VALIDATION_SPLIT_PERCENTAGE],
    )
    embeddings_sample = embeddings[mask]
    logging.info("Sampled {} embeddings".format(len(embeddings_sample)))

    # Reduce dimensionality with UMAP
    logging.info("Init of UMAP")
    umap_model = UMAP()

    # Init HDBSCAN
    # Remember to set prediction_data=True to let HDBSCAN infer labels for new data
    logging.info("Init of HDBSCAN")
    clustering_model = HDBSCAN(gen_min_span_tree=True, prediction_data=True)

    pipe = Pipeline(
        steps=[("umap", umap_model), ("hdbscan", clustering_model)], verbose=True
    )

    # specify parameters and distributions to sample from
    param_grid = {
        "umap__n_neighbors": [2, 20, 50, 100],
        "umap__min_dist": [0.0],
        "umap__n_components": [5, 10, 20],
        "hdbscan__min_samples": [10, 15, 30, 50, 75, 100],
        "hdbscan__min_cluster_size": list(range(25, 50, 25)),
        "hdbscan__cluster_selection_method": ["eom", "leaf"],
        "hdbscan__metric": ["euclidean"],
    }

    # Initialize the optimization variables
    best_score = -1
    best_params = None

    # Use ParameterSampler instead of ParameterGrid
    param_list = list(
        ParameterSampler(param_grid, n_iter=NUMBER_OF_ITERATIONS, random_state=42)
    )

    for params in param_list:
        pipe = Pipeline(
            steps=[
                ("umap", UMAP()),
                ("hdbscan", HDBSCAN(gen_min_span_tree=True, prediction_data=True)),
            ],
            verbose=True,
        )
        pipe.set_params(**params)
        pipe.fit(embeddings_sample, None)

        current_score = pipe.named_steps["hdbscan"].relative_validity_

        # Check if the current model is better than the previous best model
        if current_score > best_score:
            best_score = current_score
            best_params = params
            logging.info(f"Found params achieving DBCV score {best_score:.3f}")
            if best_score >= 0.40:
                ### Fit a model with the best parameters - only if the score is good enough
                logging.info("Creating a BERTopic model with the best parameters...")
                # Init a BERTopic model
                topic_model = create_model(
                    pipe.named_steps["umap"], pipe.named_steps["hdbscan"]
                )
                logging.info(f"BERTopic model created with DBCV score {best_score}")

                # Fit a BERTopic model to evaluate its quality
                logging.info("Fitting the model and transforming data...")
                topics, probs = topic_model.fit_transform(
                    documents,embeddings=embeddings
                )
                logging.info("BERTopic model fitted and data transformed.")

                # Store the model
                topic_model.save(
                    BEST_MODELS_PATH + f"model_{best_score}.pickle",
                    save_embedding_model=False,
                )
                topic_model.save(
                    BEST_MODELS_PATH + f"model_{best_score}.safetensors",
                    serialization="safetensors",
                    save_ctfidf=True,
                    save_embedding_model=False,
                )
                logging.info(f"Best Parameters {best_params}")
                logging.info(f"DBCV score :{best_score:.3f}")
                logging.info(f"{pipe.named_steps['hdbscan'].relative_validity_}")
                logging.info(f"Model saved in {BEST_MODELS_PATH}")

        print(params)
        print(current_score)

    logging.info("############## End :D ##############")
