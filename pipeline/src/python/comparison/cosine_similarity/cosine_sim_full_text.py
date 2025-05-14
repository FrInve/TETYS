from sentence_transformers import SentenceTransformer, util
from bertopic import BERTopic
import pandas as pd
import regex as re
import spacy


DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/25_febbraio/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

sentence_model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v1')

# Model topics
df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/12_marzo_rimozione_punteggiatura/model_0.41913836673087335.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
document_topics = model.get_document_info(documents)
#document_topics.to_csv("model_topics.csv")
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
df_cos_sim = pd.merge(left=document_topics, right=df_andrea, on='id', how='inner', suffixes=('_model', '_andrea'))
df_cos_sim.rename(columns={'model_topics': 'topics_model'}, inplace=True)
df_cos_sim.rename(columns={'topics': 'topics_andrea'}, inplace=True)

# now we need to split some strings
df_cos_sim['topics_model'] = df_cos_sim['topics_model'].apply(lambda x: x.split('-'))
#df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: x.split(';'))
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda x:  re.sub(';', " ", x))

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
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))

# Delete digits from Andrea's topics
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda x:  re.sub('\d+', " ", x))

# Delete special character
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda x:  re.sub('\-', " ", x))

# Split words
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda x: re.split(' ', x))

# Drop duplicated words
df_cos_sim['topics_andrea'] = df_cos_sim['topics_andrea'].apply(lambda x: list( dict.fromkeys(x) ))

df_cos_sim.astype(
        {
            "id": "string",
            "topics_model": "string",
            "topics_andrea": "string",
        }
)

cosine_similarities = []

for row in df_cos_sim.iterrows():
    # create a string from the list of topics
    model_topics = ' '.join(row[1]['topics_model'])
    andrea_topics = ' '.join(row[1]['topics_andrea'])

    # remove extra spaces
    " ".join(model_topics.split())
    " ".join(andrea_topics.split())

    # create the embeddings for each sentence
    model_topics_embeddings = sentence_model.encode(model_topics)
    andrea_topics_embeddings = sentence_model.encode(andrea_topics)

    # compute the similarity between the embeddings
    similarity = util.pytorch_cos_sim(model_topics_embeddings, andrea_topics_embeddings)[0][0].item()

    cosine_similarities.append(similarity)


df_cos_sim['cosine_similarity'] = cosine_similarities

df_cos_sim.to_csv("cosine_sim.csv")

print('Mean is: ', df_cos_sim['cosine_similarity'].mean())
print('Median is: ', df_cos_sim['cosine_similarity'].median())
    





