from data.estrazione_topic_andrea import get_topics as get_topics_andrea
from data.estrazione_topic_andrea import flatten_list
from data.lev_distance import min_dis
from bertopic import BERTopic
import pandas as pd
import regex as re
#import nltk
#from Levenshtein import distance

#in questo script calcoliamo l'edit distance tra topic considerando un modello trainato 
#su un documento che conteneva la concatenazione dei titoli degli articoli

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/metadata_superclean_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/13_novembre_full_titles/model_0.4132', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = model.get_document_info(documents)
document_topics = pd.concat([document_topics, df['l.id'].rename("law_id")], axis=1)
document_topics = document_topics[['law_id', 'Top_n_words']]
#remove digits
document_topics['Top_n_words'] = document_topics['Top_n_words'].apply(lambda x: re.sub('\d+', ' ', x))
#document_topics['Name'] = document_topics['Name'].apply(lambda x: re.sub('-', ' ', x))
document_topics.rename(columns={'law_id': 'id'}, inplace=True)
document_topics.rename(columns={'Top_n_words': 'model_topics'}, inplace=True)




# Andrea topics
df_andrea = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/export.csv")
df_andrea['id'] = df_andrea['id'].apply(lambda x: re.sub('"', '', x))
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub('"', '', x))

# Merge the dataframes
df_lev = pd.merge(left=document_topics, right=df_andrea, on='id', how='inner', suffixes=('_model', '_andrea'))
df_lev.rename(columns={'model_topics': 'topics_model'}, inplace=True)
df_lev.rename(columns={'topics': 'topics_andrea'}, inplace=True)

# now we need to split some strings
df_lev['topics_model'] = df_lev['topics_model'].apply(lambda x: x.split('-'))
df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: x.split(';'))

avg_edit_dist = []

for row in df_lev.iterrows():
    model_list = row[1]['topics_model']
    andrea_list = row[1]['topics_andrea']
    sum_distances = 0
#l'average edit distance in questo caso viene trovata calcolando l'edit distance tra una parola del topic del mio modello 
#e tutte le altre parole dei topic di andrea. Tra tutte queste distanze viene salvata la minore
#infine viene calcolata la media per ogni documento
    for i in range(1, len(model_list)):
        min_distance = min_dis(model_list[i], andrea_list[0])

        for j in andrea_list:
            edit_distance = min_dis(model_list[i], j)
            if edit_distance<min_distance:
                min_distance = edit_distance
        
        sum_distances += min_distance
    
    avg_distance = sum_distances/(len(model_list))
    avg_edit_dist.append(avg_distance)

df_lev['average_edit_distance'] = avg_edit_dist

df_lev.astype(
        {
            "id": "string",
            "topics_model": "string",
            "topics_andrea": "string",
            "average_edit_distance": "string",
        }
).to_csv("edit_distance.csv")
    





