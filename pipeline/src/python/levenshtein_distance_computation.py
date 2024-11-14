from data.estrazione_topic_andrea import get_topics as get_topics_andrea
from data.estrazione_topic_andrea import flatten_list
from data.lev_distance import min_dis
from bertopic import BERTopic
import pandas as pd
import regex as re
#import nltk
#from Levenshtein import distance

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
document_topics = document_topics[['law_id', 'Name']]
#remove digits
document_topics['Name'] = document_topics['Name'].apply(lambda x: re.sub('\d+', ' ', x))
document_topics['Name'] = document_topics['Name'].apply(lambda x: re.sub('-', ' ', x))
document_topics.rename(columns={'law_id': 'id'}, inplace=True)
# document topics is a df with columns:law_id and Name(which are the topics assigned by the model, divided by '_')


# Andrea topics
df_andrea = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/export.csv")
df_andrea['id'] = df_andrea['id'].apply(lambda x: re.sub('"', '', x))
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub('"', '', x))

# Merge the dataframes
df_lev = pd.merge(left=document_topics, right=df_andrea, on='id', how='inner', suffixes=('_model', '_andrea'))
df_lev.rename(columns={'Name': 'topics_model'}, inplace=True)
df_lev.rename(columns={'topics': 'topics_andrea'}, inplace=True)

# now we need to split some strings
df_lev['topics_model'] = df_lev['topics_model'].apply(lambda x: x.split('_'))
df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: x.split(';'))

#create the final df, at the end we will concatenate this df with the other one
final_df = pd.DataFrame(columns=['average_edit_distance'])

for row in df_lev.iterrows():
    model_list = row[1]['topics_model']
    andrea_list = row[1]['topics_andrea']
    sum_distances = 0
    for i in range(1, len(model_list)):
        min_distance = min_dis(model_list[i], andrea_list[0])

        for j in andrea_list:
        # calcola l'edit distance tra questa parole del topic e tutte le parole nel topic di andrea
            edit_distance = min_dis(model_list[i], j)
            if edit_distance<min_distance:
                min_distance = edit_distance
        
        sum_distances += min_distance
    
    avg_distance = sum_distances/4
    final_df['average_edit_distance'] = final_df['average_edit_distance'].append(avg_distance)

print(final_df)
    





