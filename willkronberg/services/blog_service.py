from typing import List

from atoma import parse_rss_bytes
from atoma.rss import RSSChannel, RSSItem
from aws_lambda_powertools import Logger, Tracer
from requests import Response, get
from retry import retry

from willkronberg.models.article import Article

logger = Logger(__name__)
tracer = Tracer()


class BlogService:
    """Service used to retrieve articles from my medium feed."""

    @tracer.capture_method
    def get_feed(self) -> List[Article]:
        """Retrieves and parses the Medium RSS feed and returns found articles.

        Returns:
            List[ArticleModel]: A list of articles from my feed.
        """

        response = self.__retrieve_feed__()
        feed = self.__parse_feed__(response)
        return self.__build_articles__(feed)

    @retry(tries=5, backoff=2, logger=logger)
    @tracer.capture_method
    def __retrieve_feed__(self) -> Response:
        """Retrieves my Medium RSS Feed via a HTTP Request.

        Returns:
            Response: The response received from the Medium web application.
        """

        response = get("https://medium.com/feed/@will-kronberg")
        response.raise_for_status()

        return response

    @tracer.capture_method
    def __parse_feed__(self, response: Response) -> RSSChannel:
        """Parses the RSS Feed received from Medium.

        Args:
            response (Response): The response received from Medium.

        Returns:
            RSSChannel: The parsed RSS feed.
        """

        return parse_rss_bytes(response.content)

    @tracer.capture_method
    def __build_articles__(self, feed: RSSChannel) -> List[Article]:
        """Takes the list of articles from the RSS Feed, serializes, and validates the result.

        Args:
            feed (RSSChannel): The parsed RSS feed.

        Returns:
            List[Article]: A list of articles retrieved from Medium.
        """

        return [self.__build_article__(item) for item in feed.items]

    def __build_article__(self, item: RSSItem) -> Article:
        description = item.content_encoded.split("<p>")[1].split("</p>")[0]

        # Truncate description if over 75 characters
        description = (
            (description[:72] + "...") if len(description) > 75 else description
        )

        return Article(
            id=str(item.guid),
            title=str(item.title),
            description=description,
            link=str(item.link),
            published_date=item.pub_date.isoformat(),
        )
