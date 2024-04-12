from pydantic import BaseModel
from typing import List, Tuple


class Context(BaseModel):
    name: str  # metadata - ID of context
    event: List[str]  # List[(str, str)]  # date, description
    background_data: List[str]  # List[(str, float)]  # date, value
    background_axis_name: str
