import gc
from pathlib import Path
import config as cfg
from loguru import logger
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
from datetime import datetime
import polars as pl 
from glob import glob
import torch

MAGAZINE = 'science_news'

BATCH_SIZE = 50

MAX_INPUT_TOKENS = 5000

MAX_INPUT_CHARS = MAX_INPUT_TOKENS * 4


DATASET_TEXT_FEATURE = (
    "text"  # In the dataset file, the column name that contains the text data
)


cfg_dict = cfg.MAGAZINE_CONFIG[MAGAZINE]


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

#text = df['text'].to_list()
#ids = df['id'].to_list()

model_name = "Qwen/Qwen3-0.6B"

logger.info(f'The model that will be used for summary creation is {model_name}')

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype="auto",
    device_map="auto"
)

def summarize_text(raw_text):
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
        max_new_tokens=150,
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
    logger.info(f'There are {len(filenames)} files that contain text already summaried')
    
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

    #logger.info(f'Summarizing {row['id']} : length: {len(row['text'])}')

    if len(text) > MAX_INPUT_CHARS:
        #logger.warning(f'{row['id']} text will be truncated, too long text')
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
        #logger.warning(f'Flush the cache after the execution of heavy text')
        torch.cuda.empty_cache()
        gc.collect()
        #logger.warning(f'Memory flushed')
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
        #torch.cuda.empty_cache()
        #gc.collect()

if summarization_list:
    summaries = pd.DataFrame({'id': ids, 'summary': summarization_list})
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = Path(cfg_dict['SUMMARIES_PATH']) / f'{MAGAZINE}_summaries_final_{now}.parquet'
    summaries.to_parquet(filename)
    logger.info(f'Final file created: {filename}')

logger.info('Execution finished, all the texts have been summarized')
    



