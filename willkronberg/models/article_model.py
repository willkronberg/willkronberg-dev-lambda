from pydantic import BaseModel, Field


class ArticleModel(BaseModel):
    id: str
    title: str
    description: str = Field(max_length=75)
    link: str
    published_date: str
