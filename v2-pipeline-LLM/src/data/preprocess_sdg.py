import dask.dataframe as dd
import dask.multiprocessing
from langdetect import DetectorFactory, detect
from pandas import merge, to_datetime
from src.utils import df_info

DetectorFactory.seed = 0


@df_info
def remove_nas(df):
    df = df[
        df.dc_title.notna()
        & df.abstract.notna()
        & df.prism_doi.notna()
        & df.prism_cover_date.notna()
        & df.pub_year.notna()
    ]
    return df


@df_info
def remove_duplicates(df):
    df.drop_duplicates(subset=["dc_identifier"], inplace=True)
    df.drop_duplicates(subset=["prism_doi"], inplace=True)
    return df


@df_info
def convert_datetime(df):
    df["prism_cover_date"] = to_datetime(df["prism_cover_date"])
    return df


@df_info
def select_time_window(df):
    criteria_before = df['prism_cover_date']>"2005-01-01"
    criteria_after = df['prism_cover_date']<"2024-01-01"
    df = df[criteria_before & criteria_after]

    return df

@df_info
def select_language(df):
    criteria_lang = df['language']=='eng'
    df = df[criteria_lang]

    return df


@df_info
def add_full_text(df):
    df["full_text"] = df["dc_title"] + ". " + df["abstract"]
    df["full_text"] = df["full_text"].str.lower()
    df = df.astype({"full_text": "string"})
    return df


@df_info
def start_pipeline(df):
    return df.copy()


@df_info
def select_language(df):
    df = df[df["language"] == "eng"]
    return df