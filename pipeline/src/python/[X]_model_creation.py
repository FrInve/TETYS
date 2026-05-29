import json
from bertopic.representation import MaximalMarginalRelevance
from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired
from transformers import AutoTokenizer
from transformers.pipelines import pipeline
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.model_selection import ParameterGrid,ParameterSampler
from sklearn.manifold import trustworthiness  
import numpy as np 
from loguru import logger 
import config as cfg 
import re
import spacy
from utils import preprocess_text

# Parameters used in this script can be configured in /TETYS/pipeline/src/python/config.py

MAGAZINE = 'scopus' 
cfg_dict = cfg.MAGAZINE_CONFIG[MAGAZINE] 
log_file = cfg_dict['LOG_PATH'] 

logger.add(
    str(log_file),
    rotation="10 MB",
    encoding="utf-8",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    ) 

# SAMPLE_PERCENTAGE - Percentage of sample to use during hyper-parameters fine tuning phase

# PARAMETER_PERCENTAGE - Percentage of parameter percentage to explore during hyper-parameters fine tuning phase
# Set this parameter to 1 enable the grid search

# MINIMUM_SCORE_TO_SAVE_MODEL - Minimum score below which the model has not been saved
# For the first time, it is recommended to set this parameter equal to 1 to evaluate all DBCV score.
# Based on the results, it is possible to apply an appropriate score filter

#Scopus 
SAMPLE_PERCENTAGE = 0.25
PARAMETER_PERCENTAGE = 1
MINIMUM_SCORE_TO_SAVE_MODEL = 0.30

#Science news 
#SAMPLE_PERCENTAGE = 1 
#PARAMETER_PERCENTAGE = 1 
#MINIMUM_SCORE_TO_SAVE_MODEL = 0.28

# The Guardian
#SAMPLE_PERCENTAGE = 0.4
#PARAMETER_PERCENTAGE = 1
#MINIMUM_SCORE_TO_SAVE_MODEL = 0.25


# Load data
data = np.load(cfg_dict['OUTPUT_PATH'],allow_pickle=True) 


texts = data['text'] 
embeddings = data['embedding'] 

# Add doc separator to each document for tokenization step
DOCSEP = "__DOCSEP__"
documents = [ f"{preprocess_text(text)} {DOCSEP} "  for text in texts]

# Load model hyper parameters
param_grid = cfg_dict['HYPERPARAMETER_GRID'] 
total_permutation = len(ParameterGrid(param_grid=param_grid)) * PARAMETER_PERCENTAGE 
number_of_sample = np.ceil(total_permutation) 

# Setting stop words
STOP_SET = set(STOP_WORDS) | set(cfg_dict["DOMAIN_SPECIFIC_STOP_WORDS"])

# Set the allowed Part of Speech components
ALLOWED_POS = {"NOUN",'PROPN',"ADJ"}


HYPHEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9]+")

def create_model(umap_model_, hdbscan_model_): 
    """ Create a BERTopic model with the initialized UMAP and HDBSCAN models """ 

    nlp = spacy.load("en_core_web_md", disable=["parser", "ner"])

    hyphen_token_re = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+")

    nlp.tokenizer.token_match = hyphen_token_re.match

    def pos_tokenizer(text):

        # Split the text in documents because BERTopic use the vectorizer in C-TF-Idf procedure joining the 
        # entire cluster texts creating a huge string that crash the RAM

        # We add DOCSEP to distinguish where split the text maintaining the right POS. 

        # We need to process text parts in batch e joining usefull keyword afterwards

        cluster_docs = [ cluster_doc.strip() for cluster_doc in text.split(DOCSEP.lower()) if cluster_doc.strip() ]

        if not cluster_docs:
            return []
        
        results = []

        for doc in nlp.pipe(cluster_docs,batch_size=256):
            valid_tokens = []        

            for token in doc:
                
                # Avoid to add doc separator
                if "__docsep__" in token.text.lower():
                    print("Error doc sep found")
                    continue

                if (
                    token.pos_ in ALLOWED_POS
                    and not token.is_punct
                    and not token.is_stop
                    and len(token.lemma_) > 2
                    and token.lemma_.lower() not in STOP_SET
                    and not token.is_digit
                ):
                    valid_tokens.append((token.i,token.lemma_.lower()))
            
            idxs =  [ token[0] for token in valid_tokens ]
            tokens = [ token[1] for token in valid_tokens ]   

            results.extend(tokens)
                
            # Bigrams only for the same document that have distance less than 2 words
            for i in range(len(tokens)-1):
                if idxs[i+1] - idxs[i] <= 2:
                    results.append(f"{tokens[i]}_{tokens[i+1]}")

        return results

    # Set ngram to 1 because tokenizer creates the bigrams
    # The same for stop words
    vectorizer_model = CountVectorizer(
        tokenizer=pos_tokenizer,
        stop_words=None,  
        token_pattern=None,  
        ngram_range=(1, 1),
        min_df=3  
    )
    
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True) 

    representation_model = [KeyBERTInspired(),MaximalMarginalRelevance(diversity=0.3)] 

    # Use a predefined pytorch pipeline for feature extraction to compute embeddings 
    tokenizer = AutoTokenizer.from_pretrained(cfg.EMBEDDING_MODEL) 

    embedding_model = pipeline(
        task="feature-extraction",
        model=cfg.EMBEDDING_MODEL,
        tokenizer=tokenizer,
        device='cpu',
        trust_remote_code=True
        ) 
    
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model_,  # Step 2 - Reduce dimensionality 
        hdbscan_model=hdbscan_model_, # Step 3 - Cluster reduced embeddings 
        vectorizer_model=vectorizer_model, # Step 4 - Tokenize topics 
        ctfidf_model=ctfidf_model, # Step 5 - Extract topic words 
        representation_model=representation_model, # Step 6 - (Optional) Fine-tune topic represenations 
        verbose=True
        ) 
        
    return topic_model 

# Set seed for reproducibility
np.random.seed(42)

# Set which articles select
data_mask = np.random.choice(
    [False,True],
    len(embeddings),
    p=[1-SAMPLE_PERCENTAGE,SAMPLE_PERCENTAGE]
) 

embeddings_sample = embeddings[data_mask] 
param_list = list(ParameterSampler(param_grid,number_of_sample,random_state=42)) 
RANK_PATH = cfg.RANK_DATA_FOLDER / f'{MAGAZINE}_rank.json' 

best_score = -1 
for idx, params in enumerate(param_list):

    umap_params = {k.split("__",1)[1]: v for k,v in params.items() if k.startswith("umap__")} 
    hdbscan_params = {k.split("__",1)[1]: v for k,v in params.items() if k.startswith("hdbscan__")} 
    
    logger.info("=" * 80)
    
    logger.info(f"RUN {idx} | umap_params={umap_params} | hdbscan_params={hdbscan_params}")
    
    logger.info("=" * 80)

    umap = UMAP(random_state=42)

    hdbscan = HDBSCAN(gen_min_span_tree=True,prediction_data=True)

    umap.set_params(**umap_params)

    hdbscan.set_params(**hdbscan_params)

    logger.info(f"Umap run starts")

    umap_reduction = umap.fit_transform(embeddings_sample)

    logger.info(f"Umap run finished")

    trust = trustworthiness(
        X = embeddings_sample, 
        X_embedded = umap_reduction,
        n_neighbors= umap_params['n_neighbors'],
        metric = umap_params['metric']
        ) 
    
    logger.info(f"Umap trustworthiness {trust}") 
    logger.info(f"Hdbscan run starts") 
    hdbscan.fit(umap_reduction) 
    logger.info(f"Hdbscan run finished") 
    labels = hdbscan.labels_ 
    
    logger.info(f"Hdbscan has produced {len(set(labels))} clusters") 
    
    if -1 in labels: 
        n_outlier_articles = (labels == -1).sum() 
        proportion = (n_outlier_articles/len(labels))*100 
        logger.info(f"Hdbscan has produced the outlier cluster composed by {n_outlier_articles}") 
        logger.info(f"The {proportion:.2f}%") 
        
    current_score = hdbscan.relative_validity_ 
    logger.info(f"DBCV score is: {current_score}") 
        
    if current_score > best_score and current_score > MINIMUM_SCORE_TO_SAVE_MODEL:

        if current_score > best_score:
            best_score = current_score 
            best_parameters = params 
        
        logger.info("Creating a BERTopic model") 
        model = create_model(umap_model_=umap,hdbscan_model_=hdbscan) 
        logger.info(f"BERTopic model created with DBCV score {current_score}") 
        logger.info("Fitting the model and transforming data...") 
        topics, probs = model.fit_transform(documents,embeddings=embeddings) 

        logger.info(f"DBCV score (Refitted model): {model.hdbscan_model.relative_validity_}")

        model.save(
            cfg_dict['MODEL_PATH'] / f"model_{current_score:.3f}.safetensors",
            serialization="safetensors",
            save_ctfidf=True,
            save_embedding_model=False
        )
            
        logger.info(f"Parameters {params}") 
        logger.info(f"DBCV score :{current_score:.3f}") 
        logger.info(f"Model saved in {cfg_dict['MODEL_PATH']}")

    else:
        logger.info('Score rejected') 
      
if best_score != -1: 
    rank = (best_parameters,best_score) 
    #rank_list.append(rank)

    with open(RANK_PATH,mode='r',encoding='utf-8') as file:
        old_rank = json.load(file) 
        old_rank.append(rank) 
        old_rank_sorted = sorted(old_rank,key=lambda x: x[1],reverse=True) 
        print(f"The best score parameters score is {old_rank_sorted[0][1]} with the following parameters {old_rank_sorted[0][0]} ") 
        
    with open(RANK_PATH,mode='w',encoding='utf-8') as file: 
        json.dump(old_rank_sorted,file)