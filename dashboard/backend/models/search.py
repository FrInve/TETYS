from pydantic import BaseModel


class SearchRecord(BaseModel):
    id: int
    terms: str
    relevance: float
