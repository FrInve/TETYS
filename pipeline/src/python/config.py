from pathlib import Path 

PROJ_ROOT= Path(__file__).resolve().parents[3]

PIPELINE_FOLDER = PROJ_ROOT / "pipeline"
LOGS_FOLDER = PROJ_ROOT / "logs"
SRC_FOLDER = PIPELINE_FOLDER / "src"
PYTHON_FOLDER = SRC_FOLDER / "python"
MODELS_FOLDER = PYTHON_FOLDER / "models"
DATA_FOLDER = PYTHON_FOLDER / "data"
INTERIM_DATA_FOLDER = DATA_FOLDER / "interim"
RANK_DATA_FOLDER = INTERIM_DATA_FOLDER / "rank"
PROCESSED_DATA_FOLDER = DATA_FOLDER / "processed"
RAW_DATA_FOLDER = DATA_FOLDER / "raw"
EMBEDDING_FOLDER = INTERIM_DATA_FOLDER / "embeddings"


EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Science news parameters

SCIENCE_NEWS_STOP_WORDS = ['activity','appear','carry','cause','close','detailed','discuss','end','fight','find','help','infect','insert','issue','kind','large','learn','like','look','need','news','number','overcome','play','produce','protect','publish','recent','reduce','report','research','researcher','researchers','reveal','risk','science','scientific','scientist','separate','small','someday','story','study','suggest','tighly','type','types','unvealing',
'use','watch','work',]

SCIENCE_NEWS_HYPERPARAMETERS = {
                        "umap__n_neighbors": [10,30,50],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [20,30,50,70],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}

# Scopus parameters

SCOPUS_STOP_WORDS = []

SCOPUS_HYPERPARAMETERS = {
                        "umap__n_neighbors": [10,30,50],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [20,30,50,70],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}

# The guardian parameters

THE_GUARDIAN_STOP_WORDS = []

THE_GUARDIAN_HYPERPARAMETERS = {
                        "umap__n_neighbors": [10,30,50],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [20,30,50,70],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}

# MIT parameters

MIT_STOP_WORDS = []

MIT_HYPERPARAMETERS = {
                        "umap__n_neighbors": [10,30,50],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [20,30,50,70],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}



MAGAZINE_CONFIG = {
    "the_guardian": {
        "OUTPUT_PATH": EMBEDDING_FOLDER / 'the_guardian_embeddings.npy',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'the_guardian_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'the_guardian.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'the_guardian/',
        "LOG_PATH": LOGS_FOLDER / 'the_guardian/the_guardian.log',
        "HYPERPARAMETER_GRID" : THE_GUARDIAN_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : THE_GUARDIAN_STOP_WORDS       
    },
    "mit": {
        "OUTPUT_PATH": EMBEDDING_FOLDER / 'mit_embeddings.npy',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'mit_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'mit.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'mit/',
        "LOG_PATH": LOGS_FOLDER / 'mit/mit.log',
        "HYPERPARAMETER_GRID" : MIT_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : MIT_STOP_WORDS
    },
    "science_news": {
        "OUTPUT_PATH": EMBEDDING_FOLDER / 'science_news_embeddings.npy',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'science_news_pipeline_data_correct.parquet',
        #"DATASET_PATH" : '/home/banfi/Tesi/data/processed/science_news/pipeline_data/science_news_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'science_news.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'science_news/',
        "LOG_PATH": LOGS_FOLDER / 'science_news/science_news.log',
        "HYPERPARAMETER_GRID" : SCIENCE_NEWS_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : SCIENCE_NEWS_STOP_WORDS
    },
    "scopus": {
        "OUTPUT_PATH": EMBEDDING_FOLDER / 'scopus_embeddings.npy',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'scopus_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'scopus.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'scopus/',
        "LOG_PATH": LOGS_FOLDER / 'scopus/scopus.log',
        "HYPERPARAMETER_GRID" : SCOPUS_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : SCOPUS_STOP_WORDS
    },
}