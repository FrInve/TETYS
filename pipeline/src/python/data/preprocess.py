import dask.dataframe as dd
import dask.multiprocessing
#from langdetect import DetectorFactory, detect
import pandas as pd
from pandas import merge, to_datetime
from utils import df_info
import spacy
import regex as re
import time

#DetectorFactory.seed = 0s
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
                            'vigore',  }

def concatenate_articles_ordered(group):
    # Sort articles by article number
    sorted_group = group.sort_values(by='a.number')
    # Concatenate texts and titles
    concatenated_text = ' '.join(f"{row['l.title']}: {row['a.title']}: {row['a.text']}" for _, row in sorted_group.iterrows())
    return pd.Series({'text': concatenated_text})

def concatenate_only_titles(group):
    # Sort articles by number
    sorted_group = group.sort_values(by='a.number')
    # Concatenate the titles
    concatenated_text = ' '.join(f"{row['l.title']}: {row['a.title']}" for _, row in sorted_group.iterrows())
    return pd.Series({'text': concatenated_text})

def remove_digits_stopwords_apostrophes_convert_lowercase(df):
    # convert to lowercase
    df['text'] = df['text'].apply(lambda x: x.lower())
    # remove digits
    df['text'] = df['text'].apply(lambda x:  re.sub("\d+|'", " ", x))
    # remove stopwords
    df['text'] = df['text'].apply(lambda text: " ".join(token.lemma_ for token in nlp(text) if not token.is_stop))
    return df

@df_info
def get_grouped_df_ordered(df):
    df = df.groupby(['l.id']).apply(concatenate_articles_ordered).reset_index()
    df.columns = ['l.id', 'text']
    return df

@df_info
def get_grouped_df_ordered_only_titles(df):
    df_bis = df.groupby(['l.id']).apply(concatenate_only_titles).reset_index()
    df_bis.columns = ['l.id', 'text']
    return df_bis

@df_info
def remove_nas(df):
    df = df[
        df.Title.notna()
    ]
    return df

@df_info
def clean_text_dask(df):
    dask_dataframe = dd.from_pandas(df, npartitions=8)
    t0 = time.time()
    result = dask_dataframe.map_partitions(remove_digits_stopwords_apostrophes_convert_lowercase, meta=df)
    df = result.compute()
    t1 = time.time()
    print("Time to process with Dask {}".format(t1-t0))
    return df

""""
@df_info
def remove_nas(df):
    df = df[
        df.title.notna()
        & df.abstract.notna()
        & df.doi.notna()
        & df.publish_time.notna()
    ]
    return df
"""

""""
@df_info
def remove_incomplete_dates(df):
    df = df[
        (df.publish_time != "2020")
        & (df.publish_time != "2021")
        & (df.publish_time != "2022")
    ]
    return df
"""

""""
@df_info
def remove_duplicates(df):
    df.drop_duplicates(subset=["cord_uid"], inplace=True)
    df.drop_duplicates(subset=["doi"], inplace=True)
    return df
"""

"""""
@df_info
def convert_datetime(df):
    df["publish_time"] = to_datetime(df["publish_time"])
    return df
"""

""""
@df_info
def select_time_window(df):
    df = df[df["publish_time"] > "2019-12-01"]
    return df
"""

""""
@df_info
def add_full_text(df):
    df["full_text"] = df["title"] + ". " + df["abstract"]
    df["full_text"] = df["full_text"].str.lower()
    df = df.astype({"full_text": "string"})
    return df
"""

@df_info
def start_pipeline(df):
    return df.copy()

""""
@df_info
def _select_english(df):
    df["language"] = df["full_text"].apply(detect)
    print("Found {df[df'language']!='en'].shape[0]} not in English.")
    df = df[df["language"] == "en"]
    return df
"""

""""
def detect_partition_lang(df):
    return df.apply(lambda row: detect(row["full_text"]), axis=1)


@df_info
def detect_language(df):
    ddf = dd.from_pandas(df, npartitions=8)
    result_ddf = ddf.map_partitions(detect_partition_lang, meta=("language", "string"))
    result = result_ddf.compute()
    df = merge(df, result, how="left", left_index=True, right_index=True)
    return df


@df_info
def select_language(df):
    df = df[df["language"] == "en"]
    return df
"""""
