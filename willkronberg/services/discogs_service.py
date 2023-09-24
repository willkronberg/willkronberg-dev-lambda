from typing import Dict

import requests
from aws_lambda_powertools import Logger
from pydantic import Json, SecretStr

from willkronberg.models.discogs import GetCollectionPaginatedResponse
from willkronberg.services.secrets_service import SecretsService

logger = Logger(__name__)


class DiscogsService:
    """Service used to interact with the Discogs API."""

    __user_token__: SecretStr
    __base_url__ = "https://api.discogs.com"

    def __init__(self):
        """Creates an instance of the DiscogsService"""

        secrets_service = SecretsService()
        self.__user_token__ = secrets_service.get_user_token("DiscogsPersonalAccessKey")

    def get_collection(self, page=1, per_page=1000) -> GetCollectionPaginatedResponse:
        """Retrieves a list of records that are owned by me.

        Args:
            page (int, optional): The page to retrieve records for. Defaults to 1.
            per_page (int, optional): The number of records included per page. Defaults to 1000.

        Returns:
            GetCollectionPaginatedResponse: A paginated list of records that I own.
        """
        data = self.__get__(
            url_path="users/will.kronberg/collection/folders/0/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "added",
                "sort_order": "desc",
            },
        )

        return GetCollectionPaginatedResponse.model_validate(data)

    def __get__(self, url_path: str, params: Dict[str, str] = {}) -> Json:
        """Makes authenticated HTTP Requests to the Discogs API.

        Args:
            url_path (str): The path to make the request to.
            params (Dict[str, str], optional): The parameters to include in the request. Defaults to {}.

        Returns:
            Json: A JSON representation of the response received from the Discogs API.
        """
        request_params = {"token": self.__user_token__.get_secret_value(), **params}

        response = requests.get(
            url=f"{self.__base_url__}/{url_path}",
            params=request_params,
            headers={"Accept-Encoding": "gzip", "User-Agent": "willkronberg.dev/1.0"},
        )

        response.raise_for_status()

        return response.json()
