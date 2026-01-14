import os
from transformers import AutoModel, AutoTokenizer
import torch.nn.functional as F
import gc
import torch
import config as cfg
from loguru import logger
from glob import glob
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

MAGAZINE = 'the_guardian'
cfg_dict = cfg.MAGAZINE_CONFIG[MAGAZINE]

log_file = Path(cfg.LOGS_FOLDER) / "embedding_creation.log"

logger.add(
    str(log_file),
    rotation="10 MB",
    encoding="utf-8",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"       
)

# Load summaries to embed

path_summaries = f'{cfg_dict['SUMMARIES_PATH']}/{MAGAZINE}_summaries_*.parquet'
summaries_filenames = glob(path_summaries)

if not summaries_filenames:
    logger.error(f'No summary files found, compute the summaries before compute embeddings')
    raise SystemExit(1)

logger.info(f'There are {len(summaries_filenames)} files that contain summaries')
logger.info(f'Loading files...')
dataset_list = [ pd.read_parquet(file) for file in summaries_filenames]
df = pd.concat(dataset_list)
logger.info(f'The {MAGAZINE} dataframe contains {len(df)} records')


# Load summaries already embedded

path_embeddings  = f'{cfg_dict['EMBEDDINGS_PATH']}/{MAGAZINE}_embeddings_*.npz'
embeddings_filenames = glob(path_embeddings)

if embeddings_filenames:
    summary_ids_already_embedded = []

    for file in embeddings_filenames:
        data = np.load(file,allow_pickle=False)

        if "id" in data.files:
            summary_ids_already_embedded.append(data["id"])
        else:
            logger.warning(f"File {file} does not contain 'id' key. Skipping.")

    ids_embedded = np.concatenate(summary_ids_already_embedded)
    df_to_be_embedded = df[ ~ df['id'].isin(ids_embedded)].copy()
    logger.info(f'{len(df_to_be_embedded)} summaries remain to embed')
else:
    logger.info('No embedding file found')
    df_to_be_embedded = df.copy()
    
if len(df_to_be_embedded) == 0:
    logger.info("Nothing to embed. Exiting.")
    raise SystemExit(0)

# Model 

model_path = cfg.EMBEDDING_MODEL
logger.info(f'Embeddings will be created using {model_path} model')

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained(model_path,dtype=torch.bfloat16, device_map={'': 0})
# inference mode
model.eval()

BATCH_SIZE = 1
# How many batch save the embeddigs on file
BATCH_IN_SINGLE_FILE = 5

# Compute embeddings
def encode(sentences):
    batch_size = len(sentences)
    sentences = [s+tokenizer.eos_token for s in sentences]
    tokenized_inputs = tokenizer(sentences, padding=True, return_tensors='pt', add_special_tokens=False).to(model.device)
    with torch.inference_mode():
        last_hidden_state = model(**tokenized_inputs).last_hidden_state
        eos_positions = tokenized_inputs.attention_mask.sum(dim=1) - 1
        embeddings = last_hidden_state[torch.arange(batch_size, device=model.device), eos_positions]
        embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.detach().to("cpu",dtype=torch.float32).numpy()


batch_ids = []
batch_texts = []

file_ids = []
file_texts = []
file_embeddings = []

batch_counter_in_file = 0
saved_file_counter = 0

# Save the embeddings file
def save_to_npz():
    global batch_counter_in_file, saved_file_counter, file_ids, file_texts, file_embeddings

    if not file_ids:
        return
    
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = cfg_dict['EMBEDDINGS_PATH'] / f"{MAGAZINE}_embeddings_{saved_file_counter}_{now}"
    tmp = str(filename) + "_tmp"
    logger.info(f'Saving the embeddings informations in file: {filename}')

    ids_array = np.array(file_ids)
    text_array = np.array(file_texts,dtype=object)
    emb_mat = np.vstack(file_embeddings).astype("float32",copy=False)

    np.savez_compressed(tmp,id=ids_array,text=text_array,embedding=emb_mat)
    os.replace(str(tmp)+'.npz',str(filename)+'.npz')

    batch_counter_in_file = 0
    saved_file_counter += 1

    file_ids = []
    file_texts = []
    file_embeddings = []
    

for row in df_to_be_embedded.itertuples(index=False):

    batch_texts.append(row.summary)
    batch_ids.append(row.id)

    if len(batch_texts) == BATCH_SIZE:
        emb_summaries = encode(batch_texts)
        file_ids.extend(batch_ids)
        file_texts.extend(batch_texts)
        file_embeddings.append(emb_summaries)

        batch_ids = []
        batch_texts = []

        batch_counter_in_file += 1
        
        torch.cuda.empty_cache()
        gc.collect()

    if batch_counter_in_file >= BATCH_IN_SINGLE_FILE:
        save_to_npz()

if file_ids:
    logger.info('Saving the last embeddings...')    
    emb_summaries = encode(batch_texts)
    file_ids.extend(batch_ids)
    file_texts.extend(batch_texts)
    file_embeddings.append(emb_summaries)
    save_to_npz()
    torch.cuda.empty_cache()
    gc.collect()

logger.info('Embeddings computation finished.')

