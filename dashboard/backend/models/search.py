from pydantic import BaseModel
from typing import List, Tuple


class SearchRecord(BaseModel):
    id: int
    terms: List[Tuple[str, float]]
    relevance: float
    title: str
    total_documents: int
