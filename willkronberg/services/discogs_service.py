from typing import Any, List, Dict, TypedDict
import requests
from aws_lambda_powertools import Logger

from willkronberg.constants import INVALID_CONSUMER_TOKEN
from willkronberg.services.secrets_service import SecretsService

logger = Logger(__name__)


class PaginationResponseUrls(TypedDict):
    next: str
    last: str


class PaginationResponse(TypedDict):
    items: int
    page: int
    pages: int
    per_page: int
    urls: PaginationResponseUrls


class ReleaseInstanceNote(TypedDict):
    field_id: int
    value: str


class Format(TypedDict):
    name: str
    qty: str
    text: str
    descriptions: List[str]


class Label(TypedDict):
    name: str
    catno: str
    entity_type: str
    entity_type_name: str
    id: int
    resource_url: str


class Artist(TypedDict):
    name: str
    anv: str
    join: str
    role: str
    tracks: str
    id: int
    resource_url: str


class Release(TypedDict):
    id: int
    master_id: int
    master_url: str
    resource_url: str
    thumb: str
    cover_image: str
    title: str
    year: int
    formats: List[Format]
    labels: List[Label]
    artists: List[Artist]
    genres: List[str]
    styles: List[str]


class ReleaseInstance(TypedDict):
    id: str
    instance_id: str
    date_added: str
    rating: int
    folder_id: int
    notes: ReleaseInstanceNote
    basic_information: Release


class GetCollectionResponse(TypedDict):
    releases: List[Dict[str, Any]]
    pagination: PaginationResponse


class DiscogsService:
    __user_token: str
    __base_url = "https://api.discogs.com"

    def __init__(self):
        secrets_service = SecretsService()
        self.__user_token = secrets_service.get_user_token("DiscogsPersonalAccessKey")

        if not self.__user_token:
            logger.error(self.user_token)
            raise Exception("Missing User Token")

    def get_collection(self, page=1, per_page=75):
        data: GetCollectionResponse = self.__get__(
            url_path="users/will.kronberg/collection/folders/0/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "added",
                "sort_order": "desc",
            },
        )

        return data

    def __get__(self, url_path: str, params: Dict[str, str] = {}) -> Any:
        request_params = {"token": self.__user_token, **params}

        resp = requests.get(
            url=f"{self.__base_url}/{url_path}",
            params=request_params,
            headers={"Accept-Encoding": "gzip", "User-Agent": "willkronberg.dev/1.0"},
        )

        resp.raise_for_status()

        return resp.json()
