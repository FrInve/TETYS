from bertopic import BERTopic
import pandas as pd
from scipy.cluster import hierarchy as sch

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/16_dicembre/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/20_febb_full_titles/model_0.615898690037993.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
print(model.get_topics())

model.visualize_topics().show()

model.visualize_heatmap().show()

model.visualize_documents(documents, hide_document_hover=True, hide_annotations=True).show()

#Visualize document per topics
DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/metadata_superclean_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

# Model topics
document_topics = model.get_document_info(documents)
print(document_topics['Top_n_words'])
