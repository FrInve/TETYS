from bertopic import BERTopic
import pandas as pd

DATASET_PATH = "/home/telese/TETYS/pipeline/src/python/data/processed/25_febbraio/metadata_full_titles.parquet"
DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)

df = pd.read_parquet(DATASET_PATH)
documents = df[DATASET_TEXT_FEATURE].apply(str).to_list()

model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/12_marzo_rimozione_punteggiatura/model_0.41913836673087335.safetensors', embedding_model='sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
print(model.get_topics())

model.visualize_topics().show()

model.visualize_heatmap().show()

model.visualize_barchart().show()
model.visualize_term_rank().show()
model.visualize_hierarchy().show()

print(model.get_topic_freq())

#model.visualize_documents(documents, hide_document_hover=True, hide_annotations=True).show()

# Model topics
#document_topics = model.get_document_info(documents)
# print(document_topics['Top_n_words'])
