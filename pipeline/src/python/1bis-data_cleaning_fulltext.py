import pandas as pd
from data import preprocess as prep
from neo4j_extraction.extraction_df_title_and_article_texts import giveMeDataLaws as getDataframe

if __name__ == "__main__":

    df = getDataframe()
    #df = pd.read_csv("./data/raw/2022-06-02/metadata.csv")

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

    df_clean = (
        df.pipe(prep.start_pipeline)
        .pipe(prep.get_grouped_df)
        #.pipe(prep.remove_nas)
    )

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

    df_clean.astype(
        {
            "law_id": "string",
            "text": "string",
        }
    ).to_parquet("./data/processed/metadata_clean_laws_full.parquet")

    df_clean.astype(
        {
            "law_id": "string",
            "text": "string",
        }
    ).to_csv("./data/processed/metadata_clean_laws_full.csv")

    print(df_clean)

