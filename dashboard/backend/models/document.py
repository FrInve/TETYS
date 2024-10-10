from pydantic import BaseModel


class Document(BaseModel):
    id: str
    title: str
    date: str
    content: str
    authors: str
    reference: str
    url: str
    num_of_citations: int
