from bertopic import BERTopic
import pandas as pd
import regex as re
import spacy
from gensim.models import Word2Vec

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/16_dicembre/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

def strip_string(x):
    return x.strip()

def strip_string_list(x):
    return [y.strip() for y in x]

if __name__ == "__main__":
    # Model topics
    df = pd.read_parquet(DATASET_PATH)
    documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

    model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/16_dicembre_full_titles/model_0.3441648391923259.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    document_topics = model.get_document_info(documents)
    document_topics.to_csv("model_topics.csv")
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
    df_lev['topics_model'] = df_lev['topics_model'].apply(strip_string_list)
    #df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: x.split(';'))
    df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x:  re.sub(';', " ", x))

    # Clean stopwords from Andrea's topics
    nlp = spacy.load('it_core_news_sm') 
    nlp.Defaults.stop_words |= {'abrogazione','applicazione','articolo', 'articoli', 'attuazione','clausola', 'clausole', 'codice', 'codici',
                                'comma','commissione', 'commissioni', 'd',
                                'decreti-legge','decreto', 'decreti', 'decreto-legge','decreto-legislativo','direttiva',
                                'direttive','disciplina', 'discipline', 'disposizioni',
                                'disposizione', 'esecuzione','governo', 'governi', 'g','il','italia','italy', 'italiano', 'l', 'legge', 'leggi', 
                                'legislativo','legislazione', 'legislazioni', 'materia', 'materie',
                                'ministeriale','misura','misure','modifica','modifiche',
                                'norma', 'norme', 'normativa', 'normative', 'numero','numeri', 'parlamento', 'procedimento','procedimenti', 'procedura',
                                'provvedimento', 'provvedimenti', 'procedure', 'ratifica', 'ratifiche', 'regolamenti', 
                                'regolamento','termine', 'termini', 'testi', 'testo',
                                'vigore', }
    df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))

    # Delete digits from Andrea's topics
    df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x:  re.sub('\d+', " ", x))

    # Split words
    df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(lambda x: re.split(' ', x))
    df_lev['topics_andrea'] = df_lev['topics_andrea'].apply(strip_string_list)

    # Load Word2Vec model
    model = Word2Vec.load("/home/telese/TETYS/pipeline/src/python/models/fasttext/word2vec")

    avg_cosine_sim = []

    for row in df_lev.iterrows():
        model_list = row[1]['topics_model']
        andrea_list = row[1]['topics_andrea']
        avg_sim_single = 0
    #similarità massima  
        for i in range(1, len(model_list)):
            max_sim = 0
            lunghezza = len(model_list)
            for j in andrea_list:
                try:
                    temp_sim = model.wv.similarity(model_list[i], j)
                    if temp_sim > max_sim:
                        max_sim = temp_sim
                    #print(sum_sim)
                except:
                    if lunghezza > 1:
                        lunghezza -= 1
        
        avg_distance = max_sim/lunghezza
        avg_cosine_sim.append(avg_distance)

    df_lev['average_cosine_sim'] = avg_cosine_sim

    df_lev.astype(
            {
                "id": "string",
                "topics_model": "string",
                "topics_andrea": "string",
                "average_cosine_sim": "string",
            }
    ).to_csv("cosine_sim_max.csv")
        





