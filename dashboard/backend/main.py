from fastapi import FastAPI
from typing import List
from models.topic import Topic
from models.search import SearchRecord
from models.project import Project
from models.context import Context

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "OK"}


@app.get("/info")
def read_info():
    return {"info": "info"}


@app.get("/project")
def read_project() -> List[str]:
    return ["project1", "project2", "project3"]


@app.get("/project/{project_id}")
def read_project(project_id: int) -> Project:

    return Project(
        name="project1",
        short_description="just a sentence",
        long_description="a paragraph",
        image="image_just_a_placeholder_for_a_link",
    )


@app.get("/paper")
def read_paper():
    return {"paper": "paper"}


@app.get("/context")
def read_context(project_id: int):
    return Context(
        name="context1",
        event=[("date", "description")],
        background_data=[("date", 0.0)],
        background_axis_name="Average Global Temperature",
    )


@app.get("/topic")
def search_topic(project_id: str, keywords: str) -> List[SearchRecord]:
    if keywords == "test":
        return [SearchRecord(id=1, terms="test", relevance=0.5)]
    return [
        SearchRecord(id=1, terms="test", relevance=0.5),
        SearchRecord(id=2, terms="test", relevance=0.5),
    ]


@app.get("/topic/{topic_id}")
def read_topic(project_id: str, topic_id: int) -> Topic:

    return Topic(
        id=1,
        terms=["term1", "term2"],
        start_date="2021-01-01",
        end_date="2021-01-31",
        frequency="1D",  # temporal size of one bin
        absolute_frequencies=[5, 5, 1, 0, 0, 12, 7],  # These are daily values
        relative_frequencies=[0.5, 0.5, 0.1, 0.0, 0.2, 0.24],  # These are daily values
    )


@app.get("/topic/{topic_id}/wordcloud")
def get_wordcloud(topic_id: int):
    return {"wordcloud": "wordcloud"}  # Update wordclouds


@app.post("/analysis/")
def request_analysis(project_id: int, topic_id: str, test_id: int):
    return {"analysis": "analysis"}


@app.get("/download")
def read_download():
    return {"download": "download"}
