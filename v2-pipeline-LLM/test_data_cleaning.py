#!/usr/bin/env python
# coding: utf-8
# import dask
# import dask.multiprocessing

import pandas as pd
from src.data import preprocess_sdg as prep

GROUP=2

if __name__ == "__main__":
    df = pd.read_csv(f"./data/raw/group_{GROUP}/new/test_data_2024_random_400_group_{GROUP}.csv")

    df_clean = (
        df.pipe(prep.start_pipeline)
        .pipe(prep.remove_nas)
        .pipe(prep.remove_duplicates)
        .pipe(prep.convert_datetime)
        .pipe(prep.add_full_text)
        .pipe(prep.select_language)
    )
    print(len(df_clean))
    df_clean.to_parquet(f"./data/processed/group_{GROUP}/new/test_data_2024_random_400_clean_group_{GROUP}.parquet")