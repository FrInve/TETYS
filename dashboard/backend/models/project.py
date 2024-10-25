from pydantic import BaseModel
from functools import lru_cache
from utils import logger
import os
from typing import Dict, List
from bertopic import BERTopic
from models.topic import TimeSeriesHolder
from models.context import ContextHolder
from models.document import Documents, TopicsExtractor, Document
import yaml
import pandas as pd


class Project(BaseModel):
    name: str
    short_description: str
    long_description: str
    picture: str


class FullProject:
    def __init__(
        self, name: str, short_description: str, long_description: str, picture: str
    ):
        self.name = name
        self.short_description = short_description
        self.long_description = long_description
        self.picture = picture
        self.model = None
        self.metadata = None

    def load_model(
        self,
        model_path: str,
        include_embeddings: bool = True,
        embeddings_model: str = "",
    ):
        if include_embeddings:
            self.model = BERTopic.load(model_path)
        else:
            self.model = BERTopic.load(model_path, embedding_model=embeddings_model)

    def load_time_series(self, path_abs_value: str, path_rel_value: str):
        self.time_series = TimeSeriesHolder(path_abs_value, path_rel_value)

    def load_context(
        self,
        name: str,
        background_trend_path: str,
        background_trend_title: str,
        events_path: str,
    ):
        self.context = ContextHolder(
            name, background_trend_path, background_trend_title, events_path
        )

    def load_data(
        self,
        data_path: str,
        labelled_data_path: str = None,
        id: str = None,
        title: str = None,
        date: str = None,
        content: str = None,
        authors: str = None,
        reference: str = None,
        url: str = None,
        num_of_citations: int = None,
    ):
        logger.info(f"Loading data for project '{self.name}'")
        if labelled_data_path is not None:
            if os.path.exists(labelled_data_path):
                self.data = Documents(data_path=labelled_data_path)
            else:
                logger.info(f"Labelled data not found for project '{self.name}'")
                logger.info("Extracting topics and adding them to metadata...")
                te = TopicsExtractor(data_path=data_path, model=self.model)
                te.extract_topics()
                te.add_topics_to_metadata(labelled_data_path)
                self.data = Documents(data_path=labelled_data_path)
        else:
            self.data = Documents(data_path=data_path)
        self.data.set_column_names(
            id=id,
            title=title,
            date=date,
            content=content,
            authors=authors,
            reference=reference,
            url=url,
            num_of_citations=num_of_citations,
        )

    def as_model(self) -> Project:
        return Project(
            name=self.name,
            short_description=self.short_description,
            long_description=self.long_description,
            picture=self.picture,
        )

    def get_trending_topics(self) -> List[str]:
        return self.time_series.get_trending_topics()

    def get_documents(self, topic_id: int, n: int = 10) -> list[Document]:
        return self.data.get_documents(topic_id, n)


@lru_cache()
def load_projects(path: str) -> Dict[str, FullProject]:
    projects = {}
    for project_path in os.listdir(path):
        with open(os.path.join(path, project_path, "project.yaml"), "r") as file:
            project_config = yaml.safe_load(file)
            logger.info(f"Parsed project file '{project_config['name']}'")

            project = FullProject(
                name=project_config["name"],
                short_description=project_config["short_description"],
                long_description=project_config["long_description"],
                picture=project_config["picture_path"],  # TODO Load picture in some way
            )
            project.load_model(
                os.path.join(path, project_path, project_config["model"]["model_path"]),
                project_config["model"]["include_embeddings"],
                project_config["model"]["embeddings_model"],
            )
            project.load_time_series(
                os.path.join(
                    path, project_path, project_config["trends_abs_value_path"]
                ),
                os.path.join(
                    path, project_path, project_config["trends_rel_value_path"]
                ),
            )

            try:
                project.load_context(
                    project_config["context"]["name"],
                    os.path.join(
                        path,
                        project_path,
                        project_config["context"]["background_trend_path"],
                    ),
                    project_config["context"]["background_trend_title"],
                    os.path.join(
                        path, project_path, project_config["context"]["events_path"]
                    ),
                )
            except KeyError:
                logger.info(f"No context data found for project '{project.name}'")

            try:
                column_identifier = (
                    project_config["data"]["column_identifier"]
                    if "column_identifier" in project_config["data"]
                    else None
                )
                column_title = (
                    project_config["data"]["column_title"]
                    if "column_title" in project_config["data"]
                    else None
                )
                column_date = (
                    project_config["data"]["column_date"]
                    if "column_date" in project_config["data"]
                    else None
                )
                column_content = (
                    project_config["data"]["column_content"]
                    if "column_content" in project_config["data"]
                    else None
                )
                column_authors = (
                    project_config["data"]["column_authors"]
                    if "column_authors" in project_config["data"]
                    else None
                )
                column_reference = (
                    project_config["data"]["column_reference"]
                    if "column_reference" in project_config["data"]
                    else None
                )
                column_url = (
                    project_config["data"]["column_url"]
                    if "column_url" in project_config["data"]
                    else None
                )
                column_num_of_citations = (
                    project_config["data"]["column_num_of_citations"]
                    if "column_num_of_citations" in project_config["data"]
                    else None
                )

                project.load_data(
                    os.path.join(
                        path, project_path, project_config["data"]["documents_path"]
                    ),
                    os.path.join(
                        path,
                        project_path,
                        project_config["data"]["labelled_documents_path"],
                    ),
                    id=column_identifier,
                    title=column_title,
                    date=column_date,
                    content=column_content,
                    authors=column_authors,
                    reference=column_reference,
                    url=column_url,
                    num_of_citations=column_num_of_citations,
                )
            except Exception as e:
                logger.info(
                    f"No data found for project '{project.name}' - Exception {type(e).__name__}"
                )

            projects[project.name] = project
            logger.info(f"Loaded project '{project.name}'")

    return projects
