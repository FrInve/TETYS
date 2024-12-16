#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from data import preprocess as prep
from neo4j_extraction.df_extraction import giveMeDataLawsTitles as getDataFrameTitles
from neo4j_extraction.df_extraction import giveMeDataLawsFull as getDataFrameFull
from collections import Counter
import regex as re
import spacy
import dask
import dask.multiprocessing

if __name__ == "__main__":

    df = getDataFrameFull()
    #df = pd.read_csv("./data/raw/2022-06-02/metadata.csv")
    print(df.shape)

    #Uncomment if yo are using only the titles (both laws and articles)
    df_clean = (
        df.pipe(prep.start_pipeline)
        .pipe(prep.get_grouped_df_ordered)
    )

    with dask.config.set(scheduler="processes", num_workers=8):
        df_clean_2 = (
            df_clean.pipe(prep.start_pipeline)
            .pipe(prep.clean_text_dask)
        )

    ##########
    #nlp = spacy.load('it_core_news_sm') 
    #nlp.Defaults.stop_words |= {'regolamento', 'decreto', 'legislativo', 'decreto-legislativo', 'decreto-legge', 'decreti-legge', 'normativa', 
    #                    'ministeriale', 'legislazione', 'legge', 'governo', 'articolo', 'attuazione', 'direttiva', 'comma',
    #                    'modifica', 'attuazione', 'testo', 'direttive', 'disposizione', 'numero', 'vigore', 'clausola', 'procedura', 'misura', 'l',
    #                    'il', 'codice', 'norma', 'esecuzione', 'termine', 'applicazione', 'abrogazione', 'ratifica', 'normativa', 'procedimento',
    #                    'commissione', 'direttiva', }
    # remove digits and apostrophes with blank
    #df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub("\d+|'", " ", x))
    # remove punctuation
    #df['text'] = df['text'].apply(lambda x:  re.sub("[^\w\s]", " ", x))
    # convert the whole text into lower_case
    #df_clean['text'] = df_clean['text'].apply(lambda x: x.lower())
    # remove stopwords 
    #df_clean['text'] = df_clean['text'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # Show the 100 most common words
    print('------------------------------ 100 MOST COMMON WORDS -------------------------------------')
    print(Counter(" ".join(df_clean_2["text"]).split()).most_common(100))
    print('------------------------------------------------------------------------------------------')
    ######

    df_clean_2.astype(
        {
            "text": "string",
            "l.id": "string",
        }
    ).to_parquet("./data/processed/16_dicembre/metadata_full_text.parquet")

    print(df_clean_2.head())
    print(df_clean_2.shape)

    df_clean_2.astype(
        {
            "text": "string",
            "l.id": "string",
        }
    ).to_csv("./data/processed/16_dicembre/metadata_full_text.csv")


