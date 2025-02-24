import pandas as pd
import regex as re
from collections import Counter
from matplotlib import pyplot as plt
import spacy
from bertopic import BERTopic
from Data.lev_distance import min_dis
import seaborn as sns
import numpy as np

DATASET_PATH = "Data/metadata_superclean_articles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

# import csv
df_andrea = pd.read_csv("Data/export.csv")
#replace ""
df_andrea['id'] = df_andrea['id'].apply(lambda x: re.sub('"', '', x))
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub('"', '', x))
#replace ; with " - "
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub(';', ' - ', x))

#eliminate stopwords and digits
# Clean stopwords from Andrea's topics
nlp = spacy.load('it_core_news_sm') 
nlp.Defaults.stop_words |= {'regolamento', 'decreto', 'legislativo', 'decreto-legislativo', 'decreto-legge', 'decreti-legge', 'normativa', 
                        'ministeriale', 'legislazione', 'legge', 'governo', 'articolo', 'attuazione', 'regolamento', 'direttiva', 'comma',
                        'Regolamento', 'modifica', 'Attuazione', 'testo', 'Testo', 'direttive', }
df_andrea['topics'] = df_andrea['topics'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))

# Delete digits from Andrea's topics
df_andrea['topics'] = df_andrea['topics'].apply(lambda x:  re.sub('\d+', " ", x))

df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.split(' - ', x))

# Flatten the column to a single list
all_words = [word for sublist in df_andrea['topics'] for word in sublist]

# Count the word frequencies
word_freq = Counter(all_words)

top_20_words = word_freq.most_common(40)

# Convert to a dictionary
word_freq_dict = dict(top_20_words)

# plot bar chart with frequencies
#plt.rcParams.update({'font.size': 6})
#plt.bar(range(len(word_freq_dict)), list(word_freq_dict.values()), align='center')
#plt.xticks(range(len(word_freq_dict)), list(word_freq_dict.keys()), rotation = 90)
#plt.show()

# import model
model = BERTopic.load('Modelli/13_novembre_articles/model_0.4214', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = model.get_document_info(documents)

# add the frequency of each topic
frequency = document_topics['Topic'].value_counts()
document_topics['topics_frequency'] = document_topics['Topic'].map(frequency)
unique_topics = document_topics.drop_duplicates(subset='Topic', keep='first')
unique_topics.sort_values(by = 'topics_frequency', ascending=False, inplace = True)
unique_topics = unique_topics.head(40)
df_model_final = unique_topics[['Top_n_words', 'Topic', 'topics_frequency']]
df_model_final['Top_n_words'] = df_model_final['Top_n_words'].apply(lambda x: x.split('-'))

data_edit_dis = []
#compute edit distance for every 
for row in df_model_final.iterrows():
	model_list = row[1]['Top_n_words']
	riga = []
	for key, value in word_freq_dict.items():
		min_distance = min_dis(model_list[0], key)
		sum_distances=0
		for word in model_list:
			distance = min_dis(word, key)
			if distance<min_distance:
				min_distance = distance
		riga.append(min_distance)
	data_edit_dis.append(riga)

df = pd.DataFrame(data_edit_dis)
df.to_csv('Data/heatmap_edit_distances_articles.csv')

print(df)

# plot the heatmap
#data = pd.read_csv('Data/heatmap_edit_distances.csv', index_col=1)
df.index.names = ['Model Topics']
g = sns.heatmap(df)
y_labels = df_model_final['Topic'].tolist()
y_labels = np.squeeze(y_labels)
x_labels = [key for key, value in word_freq_dict.items()]
g.set_xticks(range(len(x_labels)), labels= x_labels, rotation=0)
g.set_yticks(range(len(y_labels)), labels = y_labels, rotation = 90)
#g.set_yticklabels(y_labels, rotation=0)
#g.set_xticklabels(x_labels, rotation=90)
g.set_title('Edit distances')
plt.tight_layout()
plt.show()
