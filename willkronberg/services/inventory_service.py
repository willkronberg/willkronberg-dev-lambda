import traceback
from typing import List

from aws_lambda_powertools import Logger
from discogs_client import Client
from discogs_client.exceptions import HTTPError
from discogs_client.models import Release
from mypy_boto3_secretsmanager.type_defs import GetSecretValueResponseTypeDef

from willkronberg.constants import INVALID_CONSUMER_TOKEN
from willkronberg.services.secrets_service import SecretsService

logger = Logger(__name__)


class InventoryService:
    client: Client
    secret: GetSecretValueResponseTypeDef

    def __init__(self):
        secrets_service = SecretsService()
        self.user_token = secrets_service.get_user_token("DiscogsPersonalAccessKey")

        if not self.user_token:
            logger.error(self.user_token)
            raise Exception("Missing User Token")

        self.client = Client("Wooly/0.1", user_token=self.user_token)

    def get_inventory(self) -> List[Release]:
        """Retrieves the user's inventory"""
        try:
            me = self.client.user("will.kronberg")

            releases: List[Release] = []
            folder = me.collection_folders[0]

            for item in folder.releases.sort("added", "desc"):
                release = item.release
                my_release = {
                    "id": item.id,
                    "date_added": item.date_added.strftime("%A %B %e, %Y"),
                    "artists": release.fetch("artists"),
                    "title": release.fetch("title"),
                    "cover_image": release.fetch("thumb"),
                    "year": release.fetch("year"),
                    "url": release.fetch("master_url"),
                }

                releases.append(my_release)

            return releases
        except HTTPError as error:
            if error.msg == INVALID_CONSUMER_TOKEN:
                raise MissingDiscogsConsumerToken(error)
            else:
                traceback.print_tb(error.__traceback__)
                raise error


class MissingDiscogsConsumerToken(Exception):
    message: str

    def __init__(self, error: HTTPError):
        print(error)
        self.message = error.msg
