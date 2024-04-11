from pydantic import BaseModel
from typing import List


class Topic(BaseModel):
    id: int
    terms: List[str]
