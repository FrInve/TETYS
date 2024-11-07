from bertopic import BERTopic
import pandas as pd
from scipy.cluster import hierarchy as sch

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/metadata_clean_laws.parquet"
DATASET_TEXT_FEATURE = (
    "Title"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/berttopic_full_title_5_nov', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

print(model.get_topics())

model.visualize_topics().show()

model.visualize_heatmap().show()

#model.visualize_documents(documents).show()