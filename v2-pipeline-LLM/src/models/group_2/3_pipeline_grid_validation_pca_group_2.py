import logging

import numpy as np
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

# from numba import set_num_threads

# set_num_threads(10)

GROUP=2

if __name__ == '__main__':
    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f'./logs/group_{GROUP}/pipeline_grid_search_group_{GROUP}_pca.log', encoding='utf-8', level=logging.INFO)

    logging.info("Starting...")
    np.random.seed(777)

    embed_model = 'embeddings_sentence_transformers_allenai_specter_group_{GROUP}.npy'

    embed = f'./data/interim/group_{GROUP}/{embed_model}'

    with open(embed,'rb') as f:
        embeddings = np.load(f)
    logging.info("Data loaded")
    logging.info(f"Embedding model: {embed_model}")


    # generate random boolean mask the length of data
    mask = np.random.choice([False, True], len(embeddings), p=[0.8, 0.2])
    embeddings_sample = embeddings[mask]

    logging.info("Sampled {} embeddings".format(len(embeddings_sample)))

    # Reduce dimensionality with PCA
    logging.info("Init of PCA")
    pca_model = PCA()

    # Init HDBSCAN
    logging.info("Init of HDBSCAN")
    clustering_model = HDBSCAN(gen_min_span_tree=True)
    
    pipe = Pipeline(steps=[("pca", pca_model),
                           ("hdbscan", clustering_model)],
                           verbose=True)

    # specify parameters and distributions to sample from
    param_grid = {
                  'pca__n_components':[3,5,10,20,30],
                  'hdbscan__min_samples': [10,15,30,50,75,100,125],
                  'hdbscan__min_cluster_size': list(range(25, 501, 25)),  
                  'hdbscan__cluster_selection_method' : ['eom','leaf'],
                  'hdbscan__metric' : ['euclidean'] 
                }

    best_score = -1
    best_params = None
    for params in ParameterGrid(param_grid=param_grid):
      pipe = Pipeline(steps=[("pca", PCA()),
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
