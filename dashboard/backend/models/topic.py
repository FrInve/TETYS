from pydantic import BaseModel
from typing import List


class Topic(BaseModel):
    id: int
    terms: List[str]
    start_date: str
    end_date: str
    frequency: str
    absolute_frequencies: List[float]
    relative_frequencies: List[float]
