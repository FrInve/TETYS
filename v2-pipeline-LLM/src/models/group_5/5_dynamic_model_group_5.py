import logging
from argparse import ArgumentParser
import pandas as pd
from bertopic import BERTopic

GROUP=5

if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser(prog="TimeSeries Extraction from BERTopic",
                            description="Extract time series data from a BERTopic model")
    parser.add_argument("--bins",dest="bins",metavar='N',type=int)

    args=parser.parse_args()
    bins = args.bins if args.bins else 228

    # Set logging
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f"./logs/group_{GROUP}/dynamic_{bins}.log", encoding='utf-8', level=logging.INFO)
    logging.info(f"Set number of bins to {bins}")

    # Read abstracts
    logging.info("Loading data...")
    df = pd.read_parquet(f'./data/processed/group_{GROUP}/metadata_clean_group_{GROUP}.parquet')

    print(df.columns)
    timestamps = df.prism_cover_date.to_list()
    abstracts = df.abstract.to_list()

    print(len(timestamps))
    print(len(abstracts))

    logging.info("Data is ready.")

    # Load topic model
    logging.info("Loading topic model...")
    topic_model = BERTopic.load(f'./models/group_{GROUP}/model_group_5_dbcv_0_37', embedding_model="sentence-transformers/allenai-specter")
    logging.info("Model is ready.")

    # Generate time series data
    logging.info("Generating time series data")
    topics_ot = topic_model.topics_over_time(abstracts, timestamps, nr_bins=bins)

    logging.info("Time series data generated.")

    topics_ot['Date'] = topics_ot.Timestamp.dt.strftime('%Y/%m/%d')
    topics_ot['Date'] = pd.to_datetime(topics_ot['Date'])

    # Export raw time series data
    logging.info("Exporting data to parquet...")
    logging.info("Exporting raw data...")
    topics_ot['Topic'] = topics_ot.Topic.astype(str)
    try:
        topics_ot.to_parquet(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_raw.parquet', allow_truncated_timestamps=True)
    except:
        logging.error("Can't export to parquet")
    topics_ot.to_csv(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_raw.csv')
    logging.info("Exported raw data.")
    # Export pivoted
    logging.info("Exporting pivoted data...")
    topics_ot_pivot = topics_ot[['Topic','Frequency','Date']].pivot(index='Date',columns='Topic',values='Frequency').copy(deep=True)

    try:
        topics_ot_pivot.to_parquet(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_pivot.parquet',allow_truncated_timestamps=True)
    except:
        logging.error("Can't export to parquet")
    topics_ot_pivot.to_csv(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_pivot.csv')
    
    logging.info("Exported pivoted data.")

    # Export pivoted normalized
    logging.info("Exporting pivoted normalized data...")
    topics_ot_pivot_norm = topics_ot_pivot.div(topics_ot_pivot.sum(axis=1),axis=0).copy(deep=True)

    try:
        topics_ot_pivot_norm.to_parquet(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_pivot_norm.parquet',allow_truncated_timestamps=True)
    except:
        logging.error("Can't export to parquet")
    topics_ot_pivot_norm.to_csv(f'./data/processed/group_{GROUP}/timeseries/{bins}_dyn_pivot_norm.csv')

    logging.info("Exported pivoted normalized data.")

    logging.info("End.") 