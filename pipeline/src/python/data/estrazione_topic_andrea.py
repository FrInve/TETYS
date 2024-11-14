import pandas as pd

def flatten_list(list):
    return [item for row in list for item in row]

def remove_duplicates(list):
    seen = []
    for i in list:
        if i not in seen:
            seen.append(i)
    return seen

def get_topics():
    df = pd.read_csv("/home/telese/TETYS/pipeline/src/python/data/export.csv")

    topics = []

    for i in df.topics:
        topics.append(i)

    topics_unique = []

    for i in topics:
        x = i.split(';')
        topics_unique.append(x)

    topics_unique = flatten_list(topics_unique)

    topics_unique = remove_duplicates(topics_unique)


