from medium_api import Medium
from typing import Dict

from aws_lambda_powertools import Logger

from willkronberg.services.secrets_service import SecretsService


logger = Logger(__name__)


class BlogService:
    secret: Dict[str, str]
    client: Medium

    def __init__(self):
        secrets_service = SecretsService()
        self.secret = secrets_service.get_secret_value("Rapid-API-Key")

        if not self.secret["RAPID_API_KEY"]:
            logger.error(self.secret)
            raise Exception("Missing User Token")

        self.client = Medium(self.secret["RAPID_API_KEY"])

    def get_user_articles(self, username: str):
        user = self.client.user(username=username)

        user.fetch_articles()

        logger.info(user.articles_as_json)

        return user.articles_as_json

    def get_article_markdown(self, article_id: str) -> str:
        article = self.client.article(article_id=article_id)

        return article.markdown
