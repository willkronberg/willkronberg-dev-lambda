import requests
import atoma
from typing import List

from aws_lambda_powertools import Logger

from willkronberg.models.article_model import ArticleModel


logger = Logger(__name__)


class BlogService:
    def get_feed(self) -> List[ArticleModel]:
        response = requests.get("https://medium.com/feed/@will-kronberg")
        response.raise_for_status()
        feed = atoma.parse_rss_bytes(response.content)

        articles = []
        for item in feed.items:
            description = item.content_encoded.split("<p>")[1].split("</p>")[0]

            # Truncate description if over 50 characters
            description = (
                (description[:75] + "...") if len(description) > 75 else description
            )

            article = ArticleModel(
                id=str(item.guid),
                title=str(item.title),
                description=description,
                link=str(item.link),
                published_date=item.pub_date.isoformat(),
            )

            articles.append(article)

        return articles
