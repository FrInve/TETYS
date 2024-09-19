from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse, Response
from typing import List, Dict
from models.topic import Topic, Terms
from models.search import SearchRecord
from models.project import Project, load_projects

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


@app.get("/")
def read_root():
    return {"status": "OK"}


@app.get("/info")
def read_info():
    return {"info": "info"}


@app.get("/project")
def read_project() -> List[str]:
    return [project.name for project in projects]


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
    doi_pattern = r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b"
    doi_matches = re.findall(doi_pattern, keywords)
    if len(doi_matches) > 0:
        works = Works()
        doi = doi_matches[0]
        try:
            paper = works.doi(doi)
            keywords = paper["title"]
        except:
            pass
        keywords = paper["title"]

    model = projects[project_id].model
    topics, similarities = model.find_topics(keywords, top_n=10)

    return [
        SearchRecord(id=topic, terms=model.get_topic(topic), relevance=similarity)
        for topic, similarity in zip(topics, similarities)
    ]


@app.get("/topic/{topic_id}")
def read_topic(project_id: str, topic_id: int) -> Topic:

    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    try:
        terms = project.model.get_topic(topic_id)
        time_series = project.time_series.get_topic(topic_id)

        topic = Topic(
            id=topic_id,
            terms=terms,
            start_date=project.time_series.get_starting_date(),
            end_date=project.time_series.get_ending_date(),
            frequency=project.time_series.get_frequency(),
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
