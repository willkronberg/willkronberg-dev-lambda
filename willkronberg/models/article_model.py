from pydantic import BaseModel


class ArticleModel(BaseModel):
    id: str
    title: str
    description: str
    link: str
    published_date: str
