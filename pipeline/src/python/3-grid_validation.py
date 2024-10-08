### DEPRECATED ###
# TODO: Remove this file
# import logging

# import numpy as np
# from hdbscan import HDBSCAN, validity
# from sklearn.metrics import make_scorer
# from sklearn.model_selection import ParameterGrid
# from sklearn.pipeline import Pipeline
# from umap import UMAP

# if __name__ == "__main__":
#     # Set logging
#     logging.basicConfig(
#         format="%(asctime)s | %(levelname)s:%(message)s",
#         filename="./logs/clustering.log",
#         encoding="utf-8",
#         level=logging.INFO,
#     )
#     logging.getLogger().addHandler(logging.StreamHandler())

#     logging.info("Starting...")

#     with open("./data/interim/embeddings.npy", "rb") as f:
#         embeddings = np.load(f)
#     logging.info("Data loaded")

#     umap_model = UMAP()

#     # Init HDBSCAN
#     clustering_model = HDBSCAN(gen_min_span_tree=True)

#     pipe = Pipeline(
#         steps=[("umap", umap_model), ("hdbscan", clustering_model)], verbose=True
#     )

#     # specify parameters and distributions to sample from
#     param_grid = {
#         "umap__n_neighbors": [50],
#         "umap__min_dist": [0.0],
#         "umap__n_components": [50],
#         "hdbscan__min_samples": [10],
#         "hdbscan__min_cluster_size": [100],
#         "hdbscan__cluster_selection_method": ["leaf"],
#         "hdbscan__metric": ["euclidean"],
#     }

#     logging.info("Starting grid search")
#     best_score = -1
#     best_params = None
#     for params in ParameterGrid(param_grid=param_grid):
#         # Sample 25% of the data
#         mask = np.random.choice([False, True], len(embeddings), p=[0.75, 0.25])
#         embeddings_sample = embeddings[mask]

#         # init a pipeline
#         pipe = Pipeline(
#             steps=[
#                 ("umap", UMAP(metric="cosine")),
#                 ("hdbscan", HDBSCAN(gen_min_span_tree=True)),
#             ],
#             verbose=True,
#         )
#         pipe.set_params(**params)
#         pipe.fit(embeddings_sample, None)

#         # check if better
#         if pipe.named_steps["hdbscan"].relative_validity_ > best_score:
#             best_score = pipe.named_steps["hdbscan"].relative_validity_
#             best_params = params
#             logging.info(f"Found params achieving DBCV score {best_score:.3f}")
#         logging.info(f"Best parameters are: {best_params}")
#         logging.info(f"Best DBCV is {best_score:.3f}")

#     logging.info(f"Best Parameters {best_params}")
#     logging.info(f"DBCV score :{best_score:.3f}")
