import pandas as pd
import matplotlib 
from matplotlib import pyplot as plt
from bertopic import BERTopic

'''
df_nuovo = pd.read_csv('Data/edit_distance_articoli.csv')
df_vecchio = pd.read_csv('Data/edit_distance_articoli_vecchio.csv') 
print('Edit distance mean is ', df_nuovo['average_edit_distance'].mean())
print('Edit distance median is ', df_nuovo['average_edit_distance'].median())
print('Previous edit distance mean was ', df_vecchio['average_edit_distance'].mean())
print('Previous edit distance median was ', df_vecchio['average_edit_distance'].median())'''


model = BERTopic.load('Modelli/13_novembre_articles/model_0.4214', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

DATASET_PATH ="Data/metadata_superclean_articles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

document_topics = model.get_document_info(documents)
frequency = document_topics['Topic'].value_counts()
document_topics['topics_frequency'] = document_topics['Topic'].map(frequency)
unique_topics = document_topics.drop_duplicates(subset='Topic', keep='first')
unique_topics.sort_values(by = 'topics_frequency', ascending=False, inplace = True)
unique_topics = unique_topics.head(40)
df_model_final = unique_topics[['Top_n_words', 'Topic', 'topics_frequency']]
df_model_final.to_csv('Data/topics_modello_articoli.csv')

'''
#plot edit distance
df_nuovo['average_edit_distance'].plot.box()
plt.show()
df_vecchio['average_edit_distance'].plot.box()
plt.show()
model.visualize_heatmap().show()
'''

'''
DATASET_PATH = "Data/metadata_superclean_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('Modelli/model_0.4132', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = model.get_document_info(documents)

# add the frequency of each topic
frequency = document_topics['Topic'].value_counts()
document_topics['topics_frequency'] = document_topics['Topic'].map(frequency)
unique_topics = document_topics.drop_duplicates(subset='Topic', keep='first')
unique_topics.sort_values(by = 'topics_frequency', ascending=False, inplace = True)
unique_topics = unique_topics.head(20)
df_model_final = unique_topics[['Top_n_words', 'Topic', 'topics_frequency']]
df_model_final['Top_n_words'] = df_model_final['Top_n_words'].apply(lambda x: x.split('-'))
df_model_final.to_csv('topic_modello.csv')
'''