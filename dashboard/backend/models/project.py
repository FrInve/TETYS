from pydantic import BaseModel


class Project(BaseModel):
    name: str
    short_description: str
    long_description: str
    image: str
