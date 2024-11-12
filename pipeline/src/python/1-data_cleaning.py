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

    df = getDataFrameTitles()
    #df = pd.read_csv("./data/raw/2022-06-02/metadata.csv")
    print(df.shape)

    """ 
    df_clean = (
        df.pipe(prep.start_pipeline)
        .pipe(prep.remove_nas)
        .pipe(prep.remove_incomplete_dates)
        .pipe(prep.remove_duplicates)
        .pipe(prep.convert_datetime)
        .pipe(prep.select_time_window)
        .pipe(prep.add_full_text)
    )
    """

    #Uncomment if you are using laws' full text
    #df_clean = (
    #    df.pipe(prep.start_pipeline)
    #    .pipe(prep.get_grouped_df)
    #    #.pipe(prep.remove_nas)

    #Uncomment if you are using only laws' titles
    df_clean = (
        df.pipe(prep.start_pipeline)
    )

    #Uncomment if yo are using only the titles (both laws and articles)
    #df_clean = (
    #    df.pipe(prep.start_pipeline)
    #    .pipe(prep.get_grouped_df_ordered_only_titles)
    #)

    """"
    with dask.config.set(scheduler="processes", num_workers=8):
        df_clean_2 = (
            df_clean.pipe(prep.start_pipeline)
            .pipe(prep.detect_language)
            .pipe(prep.select_language)
        )
    """
    """
    df_clean_2.astype(
        {
            "ID": "string",
            "sha": "string",
            "source_x": "string",
            "title": "string",
            "doi": "string",
            "pmcid": "string",
            "pubmed_id": "string",
            "license": "string",
            "abstract": "string",
            "authors": "string",
            "journal": "string",
            "mag_id": "string",
            "who_covidence_id": "string",
            "arxiv_id": "string",
            "pdf_json_files": "string",
            "pmc_json_files": "string",
            "url": "string",
            "s2_id": "string",
            "full_text": "string",
            "language": "string",
        }
    ).to_parquet("./data/processed/metadata_clean.parquet")
    """

    ##########
    nlp = spacy.load('it_core_news_sm') 
    nlp.Defaults.stop_words |= {'regolamento', 'decreto', 'legislativo', 'decreto-legislativo', 'decreto-legge', 'decreti-legge', 'normativa', 
                        'ministeriale', 'legislazione', 'legge', 'governo', 'articolo', 'attuazione', 'regolamento', 'direttiva', 'comma',
                        'Regolamento', 'modifica', 'Attuazione', 'testo', 'Testo', 'direttive'}
    # remove all digits
    df_clean['text'] = df_clean['text'].apply(lambda x:  re.sub('\d+', " ", x))
    # remove punctuation
    #df['text'] = df['text'].apply(lambda x:  re.sub("[^\w\s]", " ", x))
    # find the 100 most common words
    #print(Counter(" ".join(df_clean["text"]).split()).most_common(100))
    #print('--------------------------------------------------------------------------------------------------------------------')
    # remove stopwords 
    df_clean['text'] = df_clean['text'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    # find the 100 most common words
    #print(Counter(" ".join(df_clean["text"]).split()).most_common(100))
    ######

    df_clean.astype(
        {
            "law_id": "string",
            "text": "string",
        }
    ).to_parquet("./data/processed/metadata_superclean_articles_titles.parquet")

    print(df_clean.head())
    print(df_clean.shape)

    #Uncomment to convert datafram to csv
    #df_clean.astype(
    #    {
    #        "law_id": "string",
    #        "text": "string",
    #    }
    #).to_csv("./data/processed/metadata_clean_laws_full_titles.csv")
