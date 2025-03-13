from sentence_transformers import SentenceTransformer, util
from bertopic import BERTopic
from operator import itemgetter
from tqdm import tqdm
import pandas as pd
import regex as re
import numpy as np
import spacy
import pickle


DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/25_febbraio/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

sentence_model = SentenceTransformer('embaas/sentence-transformers-multilingual-e5-large')

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

topic_model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/12_marzo_rimozione_punteggiatura/model_0.41913836673087335.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = topic_model.get_document_info(documents)
document_topics.to_csv("model_topics.csv")
document_topics = pd.concat([document_topics, df['l.id'].rename("law_id")], axis=1)
document_topics = document_topics[['law_id', 'Top_n_words', 'Topic']]
#remove digits
document_topics['Top_n_words'] = document_topics['Top_n_words'].apply(lambda x: re.sub('\d+', ' ', x))
#document_topics['Name'] = document_topics['Name'].apply(lambda x: re.sub('-', ' ', x))
document_topics.rename(columns={'law_id': 'id'}, inplace=True)
document_topics.rename(columns={'Top_n_words': 'model_topics'}, inplace=True)
document_topics.rename(columns={'Topic': 'topic_id'}, inplace=True)

# Andrea topics
df_andrea = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/export.csv")
df_andrea['id'] = df_andrea['id'].apply(lambda x: re.sub('"', '', x))
df_andrea['topics'] = df_andrea['topics'].apply(lambda x: re.sub('"', '', x))

# Merge the dataframes
df_topics_joined = pd.merge(left=document_topics, right=df_andrea, on='id', how='inner', suffixes=('_model', '_andrea'))
df_topics_joined.rename(columns={'model_topics': 'topics_model'}, inplace=True)
df_topics_joined.rename(columns={'topics': 'topics_andrea'}, inplace=True)

# now we need to split some strings
df_topics_joined['topics_model'] = df_topics_joined['topics_model'].apply(lambda x: x.split('-'))
#df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: x.split(';'))
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda x:  re.sub(';', " ", x))

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
                            'dicembre',}
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))

# Delete digits from Andrea's topics
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda x:  re.sub('\d+', " ", x))

# Delete special character
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda x:  re.sub('\-', " ", x))

# Split words
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda x: re.split(' ', x))

# Drop duplicated words
df_topics_joined['topics_andrea'] = df_topics_joined['topics_andrea'].apply(lambda x: list( dict.fromkeys(x) ))

# Start buildin the ranking matrix
list_of_matrices =[]
list_of_ranking = []
for row in tqdm(df_topics_joined.iloc[1501:].iterrows(), total=len(df_topics_joined.iloc[1501:])):
    tuple_list = []
    ranking_matrix = []
    subtopics = row[1]['topics_model']
    labels = row[1]['topics_andrea']
    # retrieve the topic id (some manipulation is needed here)
    topic_id = int("".join(str(row[1]['topic_id'])))
    # create a dictionary (subtopic: relevance)
    subtopics_dict = dict(topic_model.get_topic(topic = topic_id))
    first_row = ['law_id', 'subtopic']
    first_row.append(labels)
    ranking_matrix.append(first_row)
    for subtopic in subtopics:
        subtopic = subtopic.strip()
        # retrieve relevance for the current subtopic
        subtopic_relevance = subtopics_dict.get(subtopic)
        # compute subtopic embedding
        subtopic_embedding = sentence_model.encode(subtopic)
        # add to the matrix row the law id and the current subtopic
        matrix_row = []
        matrix_row.append(" ".join(str(row[1]['id']).split()))
        matrix_row.append(subtopic)
        for label in labels:
            # compute the label embedding
            label_embedding = sentence_model.encode(str(label))
            # compute the score (right now  is cosine_similarity*c-tf-idf of the current subtopic)
            score = float(util.pytorch_cos_sim(subtopic_embedding, label_embedding)[0][0].item()) * float(subtopic_relevance)
            tuple = (label, subtopic, score)
            tuple_list.append(tuple)
            matrix_row.append(score)
        ranking_matrix.append(matrix_row)

    #ranking_matrix = np.asmatrix(ranking_matrix)
    list_of_matrices.append(ranking_matrix)

    # create the ranking
    ranking_size = 0
    if len(labels) < 10:
        ranking_size = len(labels)
    else:
        ranking_size = 10
    ranking = []

    # sort the scores
    tuple_list.sort(key=itemgetter(2), reverse = True)
    # set_tuples = set(tuple_list)
    # delete multiple occrences of the labels

    #print('Temporary ranking:')
    #print(tuple_list[:ranking_size+1])
    tuple_list.insert(0, " ".join(str(row[1]['id']).split()))
    list_of_ranking.append(tuple_list[:ranking_size+1])

# concatenate all the dfs
df_ranking = pd.DataFrame(list_of_ranking)
df_ranking.to_csv('rankings_1500.csv')
# save the matrices
list_of_matrices = np.array(list_of_matrices, dtype=object)
np.savez_compressed('matrices_compressed_1500', list_of_matrices)
# save with pickle
with open("all_matrices_1500.pkl", "wb") as f:
    pickle.dump(list_of_matrices, f)
# df_final = pd.DataFrame.from_dict(map(dict,list_of_df))
# df_final.to_csv('all_matrices_prova.csv')





