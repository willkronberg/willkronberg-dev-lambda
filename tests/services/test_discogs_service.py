from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from willkronberg.services.discogs_service import DiscogsService


class GetResponse:
    data: Dict[str, Any]

    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


secrets_mock = Mock()

get_mock = Mock()
requests_mock = Mock()
requests_mock.get = get_mock


@pytest.fixture(autouse=True)
def run_around_tests():
    secrets_mock.reset_mock()
    get_mock.reset_mock()

    yield


@patch("willkronberg.services.discogs_service.SecretsService", secrets_mock)
@patch("willkronberg.services.discogs_service.requests", requests_mock)
def test_get_collection_no_releases():
    get_mock.return_value = GetResponse(
        data={
            "pagination": {
                "page": 1,
                "pages": 1,
                "per_page": 1000,
                "items": 0,
                "urls": {
                    "last": "https://test-last-url.com",
                    "next": "https://test-next-url.com",
                },
            },
            "releases": [],
        }
    )

    response = None
    error = None

    try:
        discogs_service = DiscogsService()
        response = discogs_service.get_collection()
    except Exception as e:
        error = e

    assert error is None
    assert response.pagination.page == 1
    assert len(response.releases) == 0


@patch("willkronberg.services.discogs_service.SecretsService", secrets_mock)
@patch("willkronberg.services.discogs_service.requests", requests_mock)
def test_get_collection_with_valid_release():
    get_mock.return_value = GetResponse(
        data={
            "pagination": {
                "page": 1,
                "pages": 1,
                "per_page": 1000,
                "items": 1,
                "urls": {
                    "last": "https://test-last-url.com",
                    "next": "https://test-next-url.com",
                },
            },
            "releases": [
                {
                    "id": 27601134,
                    "instance_id": 1461317893,
                    "date_added": "2023-09-18T09:41:08-07:00",
                    "rating": 0,
                    "basic_information": {
                        "id": 27601134,
                        "master_id": 1023676,
                        "master_url": "https://api.discogs.com/masters/1023676",
                        "resource_url": "https://api.discogs.com/releases/27601134",
                        "thumb": "https://i.discogs.com/dNCx3NEUm1P9lM8CE_FlkFx_5poIVUAmm6r0OWEIaIA/rs:fit/g:sm/q:40/h:150/w:150/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTI3NjAx/MTM0LTE2OTE0MjYz/OTktNTczOC5qcGVn.jpeg",
                        "cover_image": "https://i.discogs.com/NYSXCvlaolSTesgsXlmBnzejXkg5J5hJe0SMbe3OTtc/rs:fit/g:sm/q:90/h:597/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTI3NjAx/MTM0LTE2OTE0MjYz/OTktNTczOC5qcGVn.jpeg",
                        "title": "No Sleep",
                        "year": 2023,
                        "formats": [
                            {
                                "name": "Vinyl",
                                "qty": "1",
                                "text": "Gold Opaque",
                                "descriptions": [
                                    "LP",
                                    "Album",
                                    "Limited Edition",
                                    "Reissue",
                                    "Remastered",
                                ],
                            }
                        ],
                        "artists": [
                            {
                                "name": "Volumes (2)",
                                "anv": "",
                                "join": "",
                                "role": "",
                                "tracks": "",
                                "id": 3322647,
                                "resource_url": "https://api.discogs.com/artists/3322647",
                            }
                        ],
                        "labels": [
                            {
                                "name": "Edge Of The Earth LLC",
                                "catno": "none",
                                "entity_type": "1",
                                "entity_type_name": "Label",
                                "id": 3323034,
                                "resource_url": "https://api.discogs.com/labels/3323034",
                            }
                        ],
                        "genres": ["Rock"],
                        "styles": ["Progressive Metal", "Metalcore"],
                    },
                    "folder_id": 1,
                }
            ],
        }
    )

    response = None
    error = None

    try:
        discogs_service = DiscogsService()
        response = discogs_service.get_collection()
    except Exception as e:
        error = e

    assert error is None
    assert response.pagination.page == 1
    assert len(response.releases) == 1


@patch("willkronberg.services.discogs_service.SecretsService", secrets_mock)
@patch("willkronberg.services.discogs_service.requests", requests_mock)
def test_get_collection_with_invalid_release():
    get_mock.return_value = GetResponse(
        data={
            "pagination": {
                "page": 1,
                "pages": 1,
                "per_page": 1000,
                "items": 1,
                "urls": {
                    "last": "https://test-last-url.com",
                    "next": "https://test-next-url.com",
                },
            },
            "releases": [{id: "test-id"}],
        }
    )

    response = None
    error = None

    try:
        discogs_service = DiscogsService()
        response = discogs_service.get_collection()
    except Exception as e:
        error = e

    assert type(error) is ValidationError
    assert response is None
