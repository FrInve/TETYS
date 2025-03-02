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

    with dask.config.set(scheduler="processes", num_workers=8):
        df_clean = (
            df.pipe(prep.start_pipeline)
            .pipe(prep.get_grouped_df_ordered_only_titles)
            .pipe(prep.clean_text_dask)
        )

    '''
    with dask.config.set(scheduler="processes", num_workers=8):
        df_clean_2 = (
            df_clean.pipe(prep.start_pipeline)
            .pipe(prep.clean_text_dask)
        )
    '''

    '''
    ### check for hidden characters ###
    for text in df_clean['text'].head():
        print(repr(text))

    ##########
    nlp = spacy.load('it_core_news_sm') 
    nlp.Defaults.stop_words |= {'regolamento', 'decreto', 'legislativo', 'decreto-legislativo', 'decreto-legge', 'decreti-legge', 'normativa', 
                        'ministeriale', 'legislazione', 'legge', 'governo', 'articolo', 'attuazione', 'direttiva', 'comma',
                        'modifica', 'attuazione', 'testo', 'direttive', 'disposizione', 'numero', 'vigore', 'clausola', 'procedura', 'misura', 'l',
                        'il', 'codice', 'norma', 'esecuzione', 'termine', 'applicazione', 'abrogazione', 'ratifica', 'normativa', 'procedimento',
                        'commissione', 'direttiva'}
    # first convert to string
    df_clean['text'] = df_clean['text'].astype(str)
    # remove digits and apostrophes with blank
    df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub("\d+", "", x))
    # remove punctuation
    # df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub(r'[^\w\s]', '', x))
    # remove exactly this kind substrings
    df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub(r'\(\s*\w\s*\)', '', x))
    # remove the /n instances
    df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub(r'(\/n)', '', x))
    # convert the whole text into lower_case
    df_clean['text'] = df_clean['text'].apply(lambda x: x.lower())
    # remove stopwords 
    df_clean['text'] = df_clean['text'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # remove extra spaces
    df_clean['text'] = df_clean['text'].apply(lambda text: " ".join(text.split()))
    '''

    # Show the 100 most common words
    print('------------------------------ 100 MOST COMMON WORDS -------------------------------------')
    print(Counter(" ".join(df_clean["text"]).split()).most_common(100))
    print('------------------------------------------------------------------------------------------')
    ######
    

    df_clean.astype(
        {
            "text": "string",
            "l.id": "string",
        }
    ).to_parquet("./data/processed/25_febbraio/metadata_full_titles.parquet")

    print(df_clean.head())

    df_clean.astype(
        {
            "text": "string",
            "l.id": "string",
        }
    ).to_csv("./data/processed/25_febbraio/metadata_full_titles.csv")


