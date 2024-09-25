#!/usr/bin/env python
# coding: utf-8
# import dask
# import dask.multiprocessing

import pandas as pd
from src.data import preprocess_sdg as prep

GROUP = 1

if __name__ == "__main__":
    df = pd.read_csv(f"./data/raw/group_{GROUP}/new/group_{GROUP}_abstracts.csv")

    df_clean = (
        df.pipe(prep.start_pipeline)
        .pipe(prep.remove_nas)
        .pipe(prep.remove_duplicates)
        .pipe(prep.convert_datetime)
        .pipe(prep.select_time_window)
        .pipe(prep.add_full_text)
        .pipe(prep.select_language)
    )

    df_clean.to_parquet(f"./data/processed/group_{GROUP}/new/metadata_clean_group_{GROUP}.parquet")