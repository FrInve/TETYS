from pydantic import BaseModel
import duckdb
import pandas as pd
from utils import logging
from functools import lru_cache


class Document(BaseModel):
    id: str
    title: str
    date: str
    content: str
    authors: str
    reference: str
    url: str
    num_of_citations: int


class Documents:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.con = duckdb.connect()

    @lru_cache
    def get_documents(self, topic_id: int, n: int = 10) -> list[Document]:
        self.con.execute(
            f"SELECT * FROM read_parquet('{self.data_path}') WHERE topic = {topic_id} LIMIT {n};"
        )
        res = self.con.df()
        res = res.apply(
            lambda x: Document(
                id=x[self.col_id] if self.col_id else "",
                title=x[self.col_title] if self.col_title else "",
                date=str(x[self.col_date].year) if self.col_date else "",
                content=x[self.col_content] if self.col_content else "",
                authors=x[self.col_authors] if self.col_authors else "",
                reference=x[self.col_reference] if self.col_reference else "",
                url=x[self.col_url] if self.col_url else "",
                num_of_citations=(
                    x[self.col_num_of_citations] if self.col_num_of_citations else 0
                ),
            ),
            axis=1,
        )
        return res

    def get_first_topic_date(self, topic_id: int) -> str:
        self.con.execute(
            f"SELECT strftime(MIN({self.col_date}), '%x') FROM read_parquet('{self.data_path}') WHERE topic = {topic_id};"
        )
        res = self.con.df()
        return res.iloc[0, 0]

    def get_last_topic_date(self, topic_id: int) -> str:
        self.con.execute(
            f"SELECT strftime(MAX({self.col_date}), '%x') FROM read_parquet('{self.data_path}') WHERE topic = {topic_id};"
        )
        res = self.con.df()
        return res.iloc[0, 0]

    def set_column_names(
        self, id, title, date, content, authors, reference, url, num_of_citations
    ):
        self.col_id = id
        self.col_title = title
        self.col_date = date
        self.col_content = content
        self.col_authors = authors
        self.col_reference = reference
        self.col_url = url
        self.col_num_of_citations = num_of_citations


class TopicsExtractor:
    def __init__(self, data_path: str, model):
        self.data_path = data_path
        self.model = model

    def extract_topics(self):
        topics = self.model.topics_
        self.df_topics = pd.DataFrame(topics, columns=["Topic"])

    def add_topics_to_metadata(self, export_path: str):
        con = duckdb.connect()
        con.execute(
            f"CREATE TABLE tmp_metadata AS SELECT * FROM parquet_scan('{self.data_path}');"
        )
        logging.info("HERE 1")
        self.df_topics.to_sql("topic", con, if_exists="replace", method="multi")
        con.execute(
            f"CREATE TABLE IF NOT EXISTS metadata AS SELECT * FROM tmp_metadata LEFT JOIN topic ON tmp_metadata.rowid = topic.rowid;"
        )
        logging.info("HERE 2")
        con.execute("DROP TABLE tmp_metadata;")
        logging.info("HERE 3")
        con.execute(f"COPY metadata TO '{export_path}' (FORMAT PARQUET); ")
        logging.info("HERE 4")
        con.close()
