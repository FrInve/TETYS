import logging
import pandas as pd
import numpy as np
from hdbscan import HDBSCAN, validity
from sklearn.metrics import make_scorer
from sklearn.model_selection import ParameterGrid
from sklearn.pipeline import Pipeline
from umap import UMAP
from sklearn.decomposition import PCA
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from bertopic.representation import KeyBERTInspired
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
# from numba import set_num_threads


# set_num_threads(10)

GROUP=4

def create_model(umap_model_, hdbscan_model_):
    # Step 1 - Extract embeddings
    vectorizer_model = CountVectorizer(stop_words="english", token_pattern="(?u)\\b[\\w-]+\\b")
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    representation_model = KeyBERTInspired()

    # All steps together
    topic_model = BERTopic(
    embedding_model = SentenceTransformer("sentence-transformers/allenai-specter"),
    # embedding_model=embedding_model_,          # Step 1 - Extract embeddings
    umap_model=umap_model_,                    # Step 2 - Reduce dimensionality
    hdbscan_model=hdbscan_model_,              # Step 3 - Cluster reduced embeddings
    vectorizer_model=vectorizer_model,        # Step 4 - Tokenize topics
    ctfidf_model=ctfidf_model,                # Step 5 - Extract topic words
    representation_model=representation_model, # Step 6 - (Optional) Fine-tune topic represenations
    verbose=True
    )
    
    return topic_model

if __name__ == '__main__':
    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f'./logs/group_{GROUP}/pipeline_grid_search_group_{GROUP}_umap.log', encoding='utf-8', level=logging.INFO)

    logging.info("Starting...")
    np.random.seed(777)

    df = pd.read_parquet(f'./data/processed/group_{GROUP}/metadata_clean_group_{GROUP}.parquet')
    df = df[df.language == "eng"]
    print(len(df[df.abstract.isna()]))
    df = df[df.abstract.notna()]
    abstracts = df.abstract.to_list()
    abstracts = [str(x) for x in abstracts]
    logging.info(f"Data loaded - {len(abstracts)} abstracts available")
    print('*************************')
    print(len(abstracts))

    embed_model = f'embeddings_sentence_transformers_allenai_specter_group_{GROUP}.npy'
    embed = f'./data/interim/group_{GROUP}/embeddings_sentence_transformers_allenai_specter_group_{GROUP}.npy'

    with open(embed,'rb') as f:
        embeddings = np.load(f)
    logging.info("Data loaded")
    logging.info(f"Embedding model: {embed_model}")


    # generate random boolean mask the length of data
    mask = np.random.choice([False, True], len(embeddings), p=[0.8, 0.2])
    embeddings_sample = embeddings[mask]
    # embeddings_sample = embeddings[:10000]
    logging.info("Sampled {} embeddings".format(len(embeddings_sample)))


    # Reduce dimensionality with UMAP
    logging.info("Init of UMAP")
    #umap_model = UMAP(n_neighbors=15, min_dist=0.0, n_components=30, metric='cosine')
    umap_model = UMAP()


    # Init HDBSCAN
    logging.info("Init of HDBSCAN")
    clustering_model = HDBSCAN(gen_min_span_tree=True, prediction_data=True)
    
    pipe = Pipeline(steps=[("umap", umap_model),
                           ("hdbscan", clustering_model)],
                           verbose=True)

    # specify parameters and distributions to sample from
    param_grid = {'umap__n_neighbors':[20,50,100],
                  'umap__min_dist':[0.0],
                  'umap__n_components':[5,10,28],
                  'hdbscan__min_samples': [10,15,50,100],
                  'hdbscan__min_cluster_size': list(range(25, 50, 25)),  
                  'hdbscan__cluster_selection_method' : ['eom','leaf'],
                  'hdbscan__metric' : ['euclidean'] 
                 }

    # param_grid = {'umap__n_neighbors':[100],
    #               'umap__min_dist':[0.0],
    #               'umap__n_components':[5],
    #               'hdbscan__min_samples': [10],
    #               'hdbscan__min_cluster_size': [25],  
    #               'hdbscan__cluster_selection_method' : ['eom'],
    #               'hdbscan__metric' : ['euclidean'],
    #               'hdbscan__prediction_data':[True]
    #             }

    best_score = -1
    best_params = None
    for params in ParameterGrid(param_grid=param_grid):
      pipe = Pipeline(steps=[("umap", UMAP()),
                           ("hdbscan", HDBSCAN(gen_min_span_tree=True, prediction_data=True))],
                           verbose=True)
      pipe.set_params(**params)
      pipe.fit(embeddings_sample, None)
      if pipe.named_steps['hdbscan'].relative_validity_ > best_score:
         best_score = pipe.named_steps['hdbscan'].relative_validity_
         best_params = params
         logging.info(f"Found params achieving DBCV score {best_score:.3f}")
         if best_score >= 0.3:
            #model create
            topic_model = create_model(pipe.named_steps['umap'],pipe.named_steps['hdbscan'])
            logging.info(f"BERTopic model created with DBCV score {best_score}")

            #model fit
            logging.info("Fitting the model and transforming data...")
            print(len(abstracts))
            print(len(embeddings))
            topics, probs = topic_model.fit_transform(abstracts, embeddings=embeddings)
            logging.info("BERTopic model fitted and data transformed.")

            #model save
            topic_model.save(f'./models/group_{GROUP}/model_group_{GROUP}_dbcv_{best_score}', save_embedding_model=False)
            logging.info(f"Best Parameters {best_params}")
            logging.info(f"DBCV score :{best_score:.3f}")
            logging.info("Model saved in ./models")
      print(params)
      print(pipe.named_steps['hdbscan'].relative_validity_)

    logging.info(f"Best Parameters {best_params}")
    logging.info(f"DBCV score :{best_score:.3f}")
