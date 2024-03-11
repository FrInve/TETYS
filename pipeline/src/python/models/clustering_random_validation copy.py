import logging

import numpy as np
import pandas as pd
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import RandomizedSearchCV
from umap import UMAP

# Set logging
logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/clustering.log', encoding='utf-8', level=logging.INFO)

logging.info("Starting...")
np.random.seed(777)

with open('./data/interim/embeddings_biobert.npy','rb') as f:
    embeddings = np.load(f)
logging.info("Data loaded")


# generate random boolean mask the length of data
mask = np.random.choice([False, True], len(embeddings), p=[0.8, 0.2])
embeddings_sample = embeddings[mask]

logging.info("Sampled {} embeddings".format(len(embeddings_sample)))

# Reduce dimensionality with UMAP
logging.info("UMAP started")
umap_model = UMAP(n_neighbors=50, min_dist=0.0, n_components=100, metric='cosine')

embeddings_umap = umap_model.fit_transform(embeddings_sample)
logging.info("UMAP Finished")

values_min_samples = [10,15,30,50,75,100]
values_min_cluster_size = [100, 200, 300, 400, 500]

# Init HDBSCAN
logging.info("Init of HDBSCAN")
clustering_model = HDBSCAN(gen_min_span_tree=True).fit(embeddings_umap)


# specify parameters and distributions to sample from
param_dist = {'min_samples': values_min_samples,
              'min_cluster_size': values_min_cluster_size,  
              'cluster_selection_method' : ['eom','leaf'],
              'metric' : ['euclidean','cosine'] 
             }
SEED = 777

validity_scorer = make_scorer(validity.validity_index,greater_is_better=True)

n_iter_search = 20

# Random search
random_search = RandomizedSearchCV(clustering_model
                                   ,param_distributions=param_dist
                                   ,n_iter=n_iter_search
                                   ,scoring=validity_scorer 
                                   ,random_state=SEED)

logging.info("Random search has started")
random_search.fit(embeddings_umap)

logging.info(f"Best Parameters {random_search.best_params_}")
logging.info(f"DBCV score :{random_search.best_estimator_.relative_validity_}")
