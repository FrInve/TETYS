import logging

import joblib
import numpy as np
import pandas as pd
from dask.distributed import Client
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from umap import UMAP

if __name__ == '__main__':
    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/clustering.log', encoding='utf-8', level=logging.INFO)

    logging.info("Starting...")
    np.random.seed(777)

    ## Load dask
    #client = Client()
    #logging.info("Dask loaded")

    with open('./data/interim/embeddings_specter_climate.npy','rb') as f:
        embeddings = np.load(f)
    logging.info("Data loaded")


    # generate random boolean mask the length of data
    mask = np.random.choice([False, True], len(embeddings), p=[0.9, 0.1])
    embeddings_sample = embeddings[mask]

    logging.info("Sampled {} embeddings".format(len(embeddings_sample)))

    # Reduce dimensionality with UMAP
    logging.info("Init of UMAP")
    #umap_model = UMAP(n_neighbors=15, min_dist=0.0, n_components=30, metric='cosine')
    umap_model = UMAP()

    # embeddings_umap = umap_model.fit_transform(embeddings_sample)
    # logging.info("UMAP Finished")


    # Init HDBSCAN
    logging.info("Init of HDBSCAN")
    clustering_model = HDBSCAN(gen_min_span_tree=True)
    
    pipe = Pipeline(steps=[("umap", umap_model),
                           ("hdbscan", clustering_model)])

    # specify parameters and distributions to sample from
    param_grid = {'umap__n_neighbors':[13,14,15],
                  'umap__min_dist':[0.0,0.05],
                  'umap__n_components':[27,28,29,30],
                  'hdbscan__min_samples': [10,15],
                  'hdbscan__min_cluster_size': list(range(25, 50, 25)),  
                  'hdbscan__cluster_selection_method' : ['eom','leaf'],
                  'hdbscan__metric' : ['euclidean'] 
                }

    param_grid_old = {'umap__n_neighbors':list(range(15,50,5)),
                  'umap__min_dist':[0.0,0.05,0.1,0.2],
                  'umap__n_components':list(range(30,110,10)),
                  'hdbscan__min_samples': [10,15,30,50,75,100],
                  'hdbscan__min_cluster_size': list(range(25, 501, 25)),  
                  'hdbscan__cluster_selection_method' : ['eom','leaf'],
                  'hdbscan__metric' : ['euclidean'] 
                }

    validity_scorer = make_scorer(validity.validity_index,greater_is_better=True)


    # Random search
    grid_search = GridSearchCV(pipe
                                    ,param_grid=param_grid
                                    ,scoring=validity_scorer 
                                    ,n_jobs=28)

    logging.info("Grid search has started")
    #with joblib.parallel_backend("dask"): 
    grid_search.fit(embeddings_sample)

    logging.info(f"Best Parameters {grid_search.best_params_}")
    logging.info(f"DBCV score :{grid_search.best_estimator_.named_steps['hdbscan'].relative_validity_:.3f}")
