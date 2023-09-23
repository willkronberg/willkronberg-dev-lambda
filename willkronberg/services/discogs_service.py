from typing import Any, Dict

import requests
from aws_lambda_powertools import Logger

from willkronberg.models.discogs_model import GetCollectionPaginatedResponse
from willkronberg.services.secrets_service import SecretsService

logger = Logger(
    __name__,
)


class DiscogsService:
    __user_token__: str
    __base_url__ = "https://api.discogs.com"

    def __init__(self):
        secrets_service = SecretsService()
        self.__user_token__ = secrets_service.get_user_token("DiscogsPersonalAccessKey")

    def get_collection(self, page=1, per_page=1000) -> GetCollectionPaginatedResponse:
        data = self.__get__(
            url_path="users/will.kronberg/collection/folders/0/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "added",
                "sort_order": "desc",
            },
        )

        response = GetCollectionPaginatedResponse.model_validate(data)
        return response

    def __get__(self, url_path: str, params: Dict[str, str] = {}) -> Any:
        request_params = {"token": self.__user_token__, **params}

        resp = requests.get(
            url=f"{self.__base_url__}/{url_path}",
            params=request_params,
            headers={"Accept-Encoding": "gzip", "User-Agent": "willkronberg.dev/1.0"},
        )

        resp.raise_for_status()

        return resp.json()
