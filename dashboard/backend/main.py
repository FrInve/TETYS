from fastapi import FastAPI
from typing import List
from models.topic import Topic
from models.search import SearchRecord

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "OK"}


@app.get("/context")
def read_context():
    return {"context": "context"}


@app.get("/topic")
def search_topic(keywords: str) -> List[SearchRecord]:
    if keywords == "test":
        return [SearchRecord(id=1, terms="test", relevance=0.5)]
    return [
        SearchRecord(id=1, terms="test", relevance=0.5),
        SearchRecord(id=2, terms="test", relevance=0.5),
    ]


@app.get("/topic/{topic_id}")
def read_topic(topic_id: int) -> Topic:

    return Topic(id=1)


@app.get("/topic/{topic_id}/wordcloud")
def read_wordcloud(topic_id: int):
    return {"wordcloud": "wordcloud"}


@app.get("/analysis/")
def read_analysis():
    return {"analysis": "analysis"}
