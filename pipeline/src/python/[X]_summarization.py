import gc
from pathlib import Path
import config as cfg
from loguru import logger
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
from datetime import datetime
from glob import glob
import torch

# Select the data source from one of the following values ['science_news','the_guardian']
MAGAZINE = 'science_news'

# Set configuration params to fit the memory  
BATCH_SIZE = 1
MAX_INPUT_TOKENS = 9500
MAX_INPUT_CHARS = MAX_INPUT_TOKENS * 4

# In the dataset file, the column name that contains the text data
DATASET_TEXT_FEATURE = (
    "text"  
)

# Load the data source parameters
cfg_dict = cfg.MAGAZINE_CONFIG[MAGAZINE]

# Logger creation
log_file = Path(cfg.LOGS_FOLDER) / "summary_creation.log"

logger.add(
        str(log_file),
        rotation="10 MB",
        encoding="utf-8",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"       
)


logger.info(f'Starting summarization for {MAGAZINE} articles...')

logger.info(f'Loading dataframe ...')

df = pd.read_parquet(cfg_dict['DATASET_PATH'])

logger.info(f'The {MAGAZINE} dataset contains {len(df)} records')

logger.info(f'The model that will be used for the summarization step is {cfg.SUMMARIZATION_MODEL}')

tokenizer = AutoTokenizer.from_pretrained(cfg.SUMMARIZATION_MODEL)
model = AutoModelForCausalLM.from_pretrained(
    cfg.SUMMARIZATION_MODEL,
    dtype="auto",
    device_map="auto"
)

def summarize_text(raw_text):

    # Summarization prompt
    messages = [
    {
        "role": "user",
        "content": (
            f"""Write a concise and neutral summary of the following text.
            Use at most 3–4 sentences. Do not add comments or extra information.
            {raw_text}"""
        )
    }]

    testo = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([testo],
                              return_tensors="pt",
                              truncation=True,
                              max_length=MAX_INPUT_TOKENS).to(model.device)
    
    with torch.inference_mode():
        generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=250,
        do_sample = False,
        temperature = 0.0,
        repetition_penalty=1.05
        )
    
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    # parsing thinking content
    try:
    # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    return tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

path = f'{cfg_dict['SUMMARIES_PATH']}/{MAGAZINE}_summaries_*.parquet'
filenames = glob(path)

if filenames:
    logger.info(f'There are {len(filenames)} files that contain text already summarized')
    
    dataset_list = [ pd.read_parquet(file) for file in filenames]

    df_already_summarized = pd.concat(dataset_list)

    logger.info(f'{len(df_already_summarized)} has been already summarized')

    df_to_be_summarized = df[ ~ df['id'].isin(df_already_summarized['id']) ]

    logger.info(f'{len(df_to_be_summarized)} remaining')
else:
    logger.info(f'No files found that contain summarized texts')
    df_to_be_summarized = df.copy()

summarization_list = []
ids = []
batch_number = 0
flush_memory = False

for current_count, row in enumerate(df_to_be_summarized.itertuples(index=False), start=1):

    text = row.text
    id_ = row.id

    if len(text) > MAX_INPUT_CHARS:
        flush_memory = True

    try:
        summary = summarize_text(text)
        summarization_list.append(summary)
        ids.append(id_)
    except(torch.cuda.OutOfMemoryError):
        logger.error(f"OOM Error on ID {row.id}. Skipping this record.")
        torch.cuda.empty_cache()
        gc.collect()
        flush_memory = False
        continue

    if flush_memory:
        logger.warning(f'Flush the cache after the execution of heavy text')
        torch.cuda.empty_cache()
        gc.collect()
        logger.warning(f'Memory flushed')
        flush_memory = False
    
    if current_count % BATCH_SIZE == 0:
        summaries = pd.DataFrame({'id':ids,'summary':summarization_list})
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = cfg_dict['SUMMARIES_PATH'] / f'{MAGAZINE}_summaries_{batch_number}_{now}.parquet'
        summaries.to_parquet(filename)        
        logger.info(f'New file created: {filename}')
        batch_number += 1
        summarization_list = []
        ids = []

if summarization_list:
    summaries = pd.DataFrame({'id': ids, 'summary': summarization_list})
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = Path(cfg_dict['SUMMARIES_PATH']) / f'{MAGAZINE}_summaries_final_{now}.parquet'
    summaries.to_parquet(filename)
    logger.info(f'Final file created: {filename}')

logger.info('Execution finished, all the texts have been summarized')