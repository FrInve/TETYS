import pandas as pd
import regex as re
from collections import Counter
from matplotlib import pyplot as plt
import spacy
from bertopic import BERTopic
#from Data.lev_distance import min_dis
import seaborn as sns

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/25_febbraio/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

# import csv
df_andrea = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/export.csv")
#replace ""
df_andrea['id'] = df_andrea['id'].apply(lambda x: re.sub('"', '', x))
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub('"', '', x))
#replace ; with " - "
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub(';', ' - ', x))

#eliminate stopwords and digits
# Clean stopwords from Andrea's topics
nlp = spacy.load('it_core_news_sm') 
nlp.Defaults.stop_words |= {'abrogazione','applicazione','articolo', 'articoli', 'attuazione','clausola', 'clausole', 'codice', 'codici',
                            'comma','commissione', 'commissioni', 'd',
                            'decreti-legge','decreto', 'decreti', 'decreto-legge','decreto-legislativo','direttiva',
                            'direttive','disciplina', 'discipline', 'disposizioni',
                            'disposizione', 'esecuzione','governo', 'governi', 'g', 'il', 'italia','italy', 'italiano', 'l', 'legge', 'leggi', 
                            'legislativo','legislazione', 'legislazioni', 'materia', 'materie',
                            'ministeriale','misura','misure','modifica','modifiche',
                            'norma', 'norme', 'normativa', 'normative', 'numero','numeri', 'n', 'parlamento', 'procedimento','procedimenti', 'procedura',
                            'provvedimento', 'provvedimenti', 'procedure', 'ratifica', 'ratifiche', 'regolamenti', 
                            'regolamento','termine', 'termini', 'testi', 'testo',
                            'vigore', 'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre',
                            'dicembre', }
df_andrea['topics'] = df_andrea['topics'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))

# Delete digits from Andrea's topics
df_andrea['topics'] = df_andrea['topics'].apply(lambda x:  re.sub('\d+', " ", x))

df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.split(' - ', x))

# Flatten the column to a single list
all_words = [word for sublist in df_andrea['topics'] for word in sublist]

# Count the word frequencies
word_freq = Counter(all_words)

top_20_words = word_freq.most_common(20)

# Convert to a dictionary
word_freq_dict = dict(top_20_words)

# plot bar chart with frequencies
#plt.rcParams.update({'font.size': 6})
#plt.bar(range(len(word_freq_dict)), list(word_freq_dict.values()), align='center')
#plt.xticks(range(len(word_freq_dict)), list(word_freq_dict.keys()), rotation = 90)
#plt.show()

# import model
model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/2_mar_full_titles/model_0.4781056328616278.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = model.get_document_info(documents)

# add the frequency of each topic
frequency = document_topics['Topic'].value_counts()
document_topics['topics_frequency'] = document_topics['Topic'].map(frequency)
unique_topics = document_topics.drop_duplicates(subset='Topic', keep='first')
unique_topics.sort_values(by = 'topics_frequency', ascending=False, inplace = True)
unique_topics = unique_topics.head(20)
df_model_final = unique_topics[['Top_n_words', 'Topic', 'topics_frequency']]
df_model_final['Top_n_words'] = df_model_final['Top_n_words'].apply(lambda x: x.split('-'))
df_model_final.to_csv('freq.csv')

'''
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
df.to_csv('heatmap_edit_distances.csv')

# plot the heatmap
#data = pd.read_csv('Data/heatmap_edit_distances.csv', index_col=1)
df.index.names = ['Model Topics']
g = sns.heatmap(df)
g.set_yticklabels(df_model_final['Topic'].tolist(), rotation=0)
g.set_xticklabels((key for key, value in word_freq_dict.items()), rotation=90)
g.set_title('Edit distances')
plt.tight_layout()
plt.show()'''
