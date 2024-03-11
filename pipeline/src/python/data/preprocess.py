import dask.dataframe as dd
import dask.multiprocessing
from langdetect import DetectorFactory, detect
from pandas import merge, to_datetime

from src.utils import df_info

DetectorFactory.seed = 0


@df_info
def remove_nas(df):
    df = df[
        df.title.notna()
        & df.abstract.notna()
        & df.doi.notna()
        & df.publish_time.notna()
    ]
    return df


@df_info
def remove_incomplete_dates(df):
    df = df[
        (df.publish_time != "2020")
        & (df.publish_time != "2021")
        & (df.publish_time != "2022")
    ]
    return df


@df_info
def remove_duplicates(df):
    df.drop_duplicates(subset=["cord_uid"], inplace=True)
    df.drop_duplicates(subset=["doi"], inplace=True)
    return df


@df_info
def convert_datetime(df):
    df["publish_time"] = to_datetime(df["publish_time"])
    return df


@df_info
def select_time_window(df):
    df = df[df["publish_time"] > "2019-12-01"]
    return df


@df_info
def add_full_text(df):
    df["full_text"] = df["title"] + ". " + df["abstract"]
    df["full_text"] = df["full_text"].str.lower()
    df = df.astype({"full_text": "string"})
    return df


@df_info
def start_pipeline(df):
    return df.copy()


@df_info
def _select_english(df):
    df["language"] = df["full_text"].apply(detect)
    print("Found {df[df'language']!='en'].shape[0]} not in English.")
    df = df[df["language"] == "en"]
    return df


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
