import logging

import numpy as np
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from umap import UMAP

if __name__ == '__main__':
    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/clustering.log', encoding='utf-8', level=logging.INFO)

    logging.info("Starting...")
    np.random.seed(777)

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



    # Init HDBSCAN
    logging.info("Init of HDBSCAN")
    clustering_model = HDBSCAN(gen_min_span_tree=True)
    
    pipe = Pipeline(steps=[("umap", umap_model),
                           ("hdbscan", clustering_model)],
                           verbose=True)

    # specify parameters and distributions to sample from
    param_grid = {'umap__n_neighbors':[2,20,100],
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

    best_score = 0
    best_params = None
    for params in ParameterGrid(param_grid=param_grid):
      pipe = Pipeline(steps=[("umap", UMAP()),
                           ("hdbscan", HDBSCAN(gen_min_span_tree=True))],
                           verbose=True)
      pipe.set_params(**params)
      pipe.fit(embeddings_sample, None)
      if pipe.named_steps['hdbscan'].relative_validity_ > best_score:
         best_score = pipe.named_steps['hdbscan'].relative_validity_
         best_params = params
         logging.info(f"Found params achieving DBCV score {best_score:.3f}")
      print(params)
      print(pipe.named_steps['hdbscan'].relative_validity_)

    logging.info(f"Best Parameters {best_params}")
    logging.info(f"DBCV score :{best_score:.3f}")
