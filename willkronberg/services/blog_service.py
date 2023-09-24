import requests
import atoma
from typing import List

from aws_lambda_powertools import Logger

from willkronberg.models.article import Article


logger = Logger(__name__)


class BlogService:
    """Service used to retrieve articles from my medium feed."""

    def get_feed(self) -> List[Article]:
        """Retrieves and parses the Medium RSS feed and returns found articles.

        Returns:
            List[ArticleModel]: A list of articles from my feed.
        """
        response = requests.get("https://medium.com/feed/@will-kronberg")
        response.raise_for_status()
        feed = atoma.parse_rss_bytes(response.content)

        articles = []
        for item in feed.items:
            description = item.content_encoded.split("<p>")[1].split("</p>")[0]

            # Truncate description if over 75 characters
            description = (
                (description[:72] + "...") if len(description) > 75 else description
            )

            article = Article(
                id=str(item.guid),
                title=str(item.title),
                description=description,
                link=str(item.link),
                published_date=item.pub_date.isoformat(),
            )

            articles.append(article)

        return articles
