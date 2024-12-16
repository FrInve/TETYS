from bertopic import BERTopic
import pandas as pd
from scipy.cluster import hierarchy as sch

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/metadata_superclean_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/15_dicembre_full_titles/model_0.5746', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

print(model.get_topics())

model.visualize_topics().show()

model.visualize_heatmap().show()

#model.visualize_documents(documents).show()
