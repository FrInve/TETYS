from bertopic import BERTopic
import pandas as pd

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/maggio/metadata_titles_1948.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/26_aprile_1948/model_0.6091000213779713.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')


model.visualize_topics().show()

model.visualize_heatmap().show()

model.visualize_barchart().show()
model.visualize_term_rank().show()
model.visualize_hierarchy().show()

print(model.get_topic_freq())
print(model.get_topics())

model.visualize_documents(documents, hide_document_hover=True, hide_annotations=True)

# Model topics
document_topics = model.get_document_info(documents)
print(document_topics['Top_n_words'])
