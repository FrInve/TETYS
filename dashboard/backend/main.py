from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Annotated
from models.topic import Topic, Terms
from models.document import Document
from models.search import SearchRecord
from models.project import Project, load_projects

import uvicorn

# from models.context import Context
from models.analysis import *
from models.settings import get_settings
from wordcloud import WordCloud
from crossref.restful import Works
import re

### State of the application ###
projects: Dict[str, Project] = load_projects(get_settings().path_projects)


### Endpoints ###

app = FastAPI(default_response_class=ORJSONResponse)

### CORS ###
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "OK"}


@app.get("/info")
def read_info():
    return {"info": "info"}


@app.get("/project")
def read_project() -> List[str]:
    return [project.name for project in projects.values()]


@app.get("/project/{project_id}/trending")
def get_trending_topics(project_id: str) -> List[str]:
    project = projects[project_id]
    trending_topics = project.get_trending_topics()
    return trending_topics


@app.get("/project/{project_id}")
def read_project(project_id: str) -> Project:
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id].as_model()


# @app.get("/paper")
# def read_paper():
#     return {"paper": "paper"}


# @app.get("/context")
# def read_context(project_id: str) -> Context:
#     if project_id not in projects:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return projects[project_id].context.to_model()


@app.get("/topic")
async def search_topic(project_id: str, keywords: str) -> List[SearchRecord]:
    # doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b" # This is wrong
    # doi_pattern = r"/^10\.\d{4,9}\/[-._;()/:A-Z0-9]+$/i" # This is from Crossref, but not for Python
    doi_pattern = r"\b10\.\d{4,9}/[-.;()/:\w]+"
    doi_matches = re.findall(doi_pattern, keywords)
    if len(doi_matches) > 0:
        works = Works()
        doi = doi_matches[0]
        try:
            paper = works.doi(doi)
            keywords = paper["title"][0]
        except:
            pass
        # keywords = paper["title"]

    model = projects[project_id].model
    time_series = projects[project_id].time_series
    topics, similarities = model.find_topics(keywords, top_n=10)

    titles = [
        ", ".join([term[0].capitalize() for term in model.get_topic(topic)[:3]])
        for topic in topics
    ]
    total_documents = [time_series.get_total_documents(topic) for topic in topics]

    return [
        SearchRecord(
            id=topic,
            terms=model.get_topic(topic),
            relevance=similarity,
            title=title,
            total_documents=total_docs,
        )
        for topic, similarity, title, total_docs in zip(
            topics, similarities, titles, total_documents
        )
    ]


@app.get("/topic/{topic_id}")
async def read_topic(
    project_id: str,
    topic_id: int,
    resolution: Annotated[str | None, Query(regex="^\d+[a-zA-Z]$")] = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Topic:

    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    try:
        terms = project.model.get_topic(topic_id)

        # Set default values
        if resolution is None:
            resolution = project.time_series.get_frequency()
            if resolution is None:
                resolution = "28"  # default resolution
        if start_date is None:
            start_date = project.time_series.get_starting_date()
        if end_date is None:
            end_date = project.time_series.get_ending_date()

        time_series = project.time_series.get_topic(
            topic_id, resolution, start_date, end_date
        )

        topic = Topic(
            id=topic_id,
            title=", ".join([term[0].capitalize() for term in terms[:3]]),
            terms=terms,
            total_documents=project.time_series.get_total_documents(topic_id),
            start_date=start_date,
            end_date=end_date,
            frequency=resolution,
            absolute_frequencies=time_series[0],
            relative_frequencies=time_series[1],
            rankings=time_series[2],
        )
        return topic
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic_id}' not found for project '{project_id}'",
        )


@app.get(
    "/topic/{topic_id}/wordcloud",
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "WordCloud of the topic",
        },
        404: {"description": "Topic not found"},
    },
    response_class=Response,
)
def get_wordcloud(topic_id: int, project_id: str) -> str:
    model = projects[project_id].model
    text = {word: value for word, value in model.get_topic(topic_id)}
    wc = WordCloud(background_color="black", max_words=50)
    wc.generate_from_frequencies(text)
    return Response(content=wc.to_svg(), media_type="image/svg+xml")


@app.get(
    "/topic/{topic_id}/terms",
    responses={
        200: {"description": "List of terms of the topic"},
        404: {"description": "Topic not found"},
    },
)
def get_terms(topic_id: int, project_id: str) -> Terms:
    terms = projects[project_id].model.get_topic(topic_id)
    return Terms(id=topic_id, terms=terms)


@app.get(
    "/topic/{topic_id}/documents",
    responses={
        200: {"description": "List of documents of the topic"},
        404: {"description": "Topic not found"},
    },
)
async def get_relevant_documents_for_topic(
    topic_id: int, project_id: str, size: int | None = 5
) -> List[Document]:
    """
    docs = [
        Document(
            id=str(i),
            title="title",
            date="1970-01-01",
            content="content",
            authors="authors",
            reference="reference",
            url="url",
            num_of_citations=0,
        )
        for i in range(size)
    ]
    return docs
    """
    project = projects[project_id]
    return project.get_documents(topic_id, size)


@app.get("/analysis/")
def read_analysis(project_id: str) -> List[str]:
    return ["single_topic-two_intervals", "single_topic-multiple_intervals"]


@app.post("/analysis/single_topic-two_intervals")
def request_test_single_topic_two_intervals(
    form: SingleTopicTwoIntervalTestForm,
) -> TestResult:
    test = SingleTopicTwoIntervalTest(form)
    test.compute()
    return test.get_result()


@app.post("/analysis/single_topic-multiple_intervals")
def request_test_single_topic_multiple_intervals(
    form: SingleTopicMultipleIntervalTestForm,
) -> TestResult:
    test = SingleTopicMultipleIntervalTest(form)
    test.compute()
    return test.get_result()


@app.get("/download")
def read_download():
    return {"download": "download"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
