from pydantic import BaseModel
from functools import lru_cache
from utils import logger
import os
from typing import Dict, List
from bertopic import BERTopic
from models.topic import TimeSeriesHolder
from models.context import ContextHolder
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

    def as_model(self) -> Project:
        return Project(
            name=self.name,
            short_description=self.short_description,
            long_description=self.long_description,
            picture=self.picture,
        )

    def get_trending_topics(self) -> List[str]:
        return self.time_series.get_trending_topics()


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

            projects[project.name] = project
            logger.info(f"Loaded project '{project.name}'")

    return projects
