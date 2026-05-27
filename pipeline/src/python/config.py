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
SUMMARIES_FOLDER = INTERIM_DATA_FOLDER / "summaries"
SUMMARIES_THE_GUARDIAN_FOLDER = SUMMARIES_FOLDER / "the_guardian"
SUMMARIES_SCIENCE_NEWS_FOLDER = SUMMARIES_FOLDER / "science_news"
EMBEDDING_SCIENCE_NEWS_FOLDER = EMBEDDING_FOLDER / "science_news"
EMBEDDING_SCOPUS_FOLDER = EMBEDDING_FOLDER / "scopus"
EMBEDDING_THE_GUARDIAN_FOLDER = EMBEDDING_FOLDER / "the_guardian"

EMBEDDING_MODEL = 'codefuse-ai/F2LLM-4B'

########################################################### PARAMETERS ###########################################################
#UMAP
# 1) umap__n_neighbors 
# Quanti vicini considerare per creare il grafo per costruire lo spazio vettoriale a bassa dimensionalità 
# ( + è alto più si ha una visione globale, + è basso più si ha una visione locale dei cluster)
#
# 2) umap__min_dist
#  è la distanza minima ammessa tra due punti nello spazio a bassa dimensionalità (proiezione)
# 
# 3) umap__n_components
#  numero di dimensioni della proiezione
#HDBSCAN
# hdbscan__min_samples
# determina quanto un punto deve essere in una zona densa per non essere considerato rumore 
# (+ è alto meno è permissivo con il rumore, + è basso e più è permissivo)
# 
# hdbscan__min_cluster_size
# minimo numero di elementi per considerare un cluster
# 
# hdbscan__cluster_selection_method
# determina come scegliere i cluster partendo dalla struttura gerarchica che crea l'algoritmo 
# ( leaf parte dalle foglie, eom (exceed of mass) utilizza un metodo statistico ) 
# 
# hdbscan__metric
# metrica di distanza adottata nel clustering

#Consigli:
#- Utilizzare cosine in Umap e euclidian in hdbscan

##################################################################################################################################

# Science news parameters

SCIENCE_NEWS_STOP_WORDS = {'activity','appear','carry','cause','close','detailed','discuss','end','fight','find','help','infect','insert','issue','kind','large','learn','like','look','need','news','number','overcome','play','produce','protect','publish','recent','reduce','report','research','researcher','researchers','reveal','risk','science','scientific','scientist','separate','small','someday','story','study','suggest','tighly','type','types','unvealing',
'use','watch','work'}

SCIENCE_NEWS_HYPERPARAMETERS = {
                        "umap__n_neighbors": [10,15,30,50],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],                        
                        "umap__metric": ['cosine'],                  
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [10,20,30,50,70],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}

# Scopus parameters

SCOPUS_STOP_WORDS = {"form", "factor", "case", "study", "site", "model",
    "addition", "result", "data", "analysis", "level",
    "rate", "number", "type", "role", "effect", "use",
    "year", "group", "method", "sample", "period","non"}

SCOPUS_HYPERPARAMETERS = {
                        "umap__n_neighbors": [50,60,70],
                        "umap__min_dist": [0.0,0.05],
                        "umap__n_components": [10,15,20,25,30],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [5,10,15,20,25],
                        "hdbscan__min_cluster_size": [100,110,120],
                        "hdbscan__cluster_selection_method": ["eom","leaf"],
                        "hdbscan__metric": ["euclidean"],
}


# The guardian parameters

THE_GUARDIAN_STOP_WORDS = {}

THE_GUARDIAN_HYPERPARAMETERS = {
                        "umap__n_neighbors": [30,50,60],
                        "umap__min_dist": [0.0],
                        "umap__n_components": [10,15,20,25],
                        "umap__metric": ['cosine'],
                        "hdbscan__min_samples": [10,15,20],
                        "hdbscan__min_cluster_size": [50,70],
                        "hdbscan__cluster_selection_method": ["eom"],
                        "hdbscan__metric": ["euclidean"],
}



MAGAZINE_CONFIG = {
    "the_guardian": {
        "OUTPUT_PATH": EMBEDDING_THE_GUARDIAN_FOLDER / 'the_guardian_embeddings_4B_aggregation_with_filter.npz',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'the_guardian_pipeline_data_summary_filter.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'the_guardian.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'the_guardian/',
        "LOG_PATH": LOGS_FOLDER / 'the_guardian/the_guardian.log',
        "HYPERPARAMETER_GRID" : THE_GUARDIAN_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : THE_GUARDIAN_STOP_WORDS,
        "SUMMARIES_PATH" : SUMMARIES_THE_GUARDIAN_FOLDER,
        "EMBEDDINGS_PATH": EMBEDDING_THE_GUARDIAN_FOLDER,
        "REFERENCE_MODEL" : MODELS_FOLDER / 'the_guardian/model_0.265_new4.safetensors'
    },
    "science_news": {
        "OUTPUT_PATH": EMBEDDING_SCIENCE_NEWS_FOLDER / 'science_news_embeddings_4B_aggregation.npz',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'science_news_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'science_news.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'science_news/',
        "LOG_PATH": LOGS_FOLDER / 'science_news/science_news.log',
        "HYPERPARAMETER_GRID" : SCIENCE_NEWS_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : SCIENCE_NEWS_STOP_WORDS,
        "SUMMARIES_PATH" : SUMMARIES_SCIENCE_NEWS_FOLDER,
        "EMBEDDINGS_PATH" : EMBEDDING_SCIENCE_NEWS_FOLDER,
        "REFERENCE_MODEL" : MODELS_FOLDER / 'science_news/model_0.299_new4.safetensors'
    },
    "scopus": {
        "OUTPUT_PATH": EMBEDDING_SCOPUS_FOLDER / 'scopus_embeddings_4B_aggregation.npz',
        "DATASET_PATH" : RAW_DATA_FOLDER / 'scopus_pipeline_data.parquet',
        "PROCESSED_PATH": PROCESSED_DATA_FOLDER / 'scopus.parquet',
        "MODEL_PATH": MODELS_FOLDER / 'scopus/',
        "LOG_PATH": LOGS_FOLDER / 'scopus/scopus.log',
        "HYPERPARAMETER_GRID" : SCOPUS_HYPERPARAMETERS,
        "DOMAIN_SPECIFIC_STOP_WORDS" : SCOPUS_STOP_WORDS,
        "EMBEDDINGS_PATH" : EMBEDDING_SCOPUS_FOLDER,
        "REFERENCE_MODEL" : MODELS_FOLDER / 'scopus/model_0.363_new4.safetensors'
    },
}