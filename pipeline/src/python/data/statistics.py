import pandas as pd
from collections import Counter
import regex as re
import spacy

if __name__ == "__main__":
    df = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/processed/metadata_clean_laws_full_titles.csv")
    nlp = spacy.load('it_core_news_sm') 
    custom_stopwords = ['regolamento', 'decreto', 'legislativo', 'decreto-legislativo', 'decreto-legge', 'decreti-legge', 'normativa', 
                        'ministeriale', 'legislazione', 'legge', 'governo', 'articolo', 'attuazione', 'regolamento', 'direttiva', 'comma'
                        'Regolamento', 'modifica', 'Attuazione']
    for w in custom_stopwords:
        nlp.vocab[w].is_stop = True
    # remove all digits
    df['text'] = df['text'].apply(lambda x:  re.sub('(?<!-)\b\d+\b', " ", x))
    # remove punctuation
    df['text'] = df['text'].apply(lambda x:  re.sub("[^\w\s]", " ", x))
    # remove stopwords 
    #df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if not is_stopword(word)]))
    df['text'] = df['text'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # find the 100 most common words
    #print(Counter(" ".join(df["text"]).split()).most_common(100))

    #save as parquet
    df.astype(
        {
            "law_id": "string",
            "text": "string",
        }
    ).to_parquet("/home/telese/TETYS/pipeline/src/python/data/processed/metadata_superclean_laws_full_titles.parquet")


