import json

from unittest.mock import Mock, patch

from willkronberg.handlers.get_collection_handler import (
    get_collection_handler,
)
from tests.fixtures.lambda_context import lambda_context
from willkronberg.models.discogs import (
    GetCollectionPaginatedResponse,
    PaginationResponse,
    PaginationResponseUrls,
    ReleaseInstance,
)

get_collection_mock = Mock()
discogs_service_mock = Mock()
discogs_service_mock().get_collection = get_collection_mock


@patch(
    "willkronberg.handlers.get_collection_handler.DiscogsService",
    discogs_service_mock,
)
def test_get_collection_handler_success_no_releases(
    lambda_context: lambda_context,
):
    response = None
    error = None

    get_collection_mock.return_value = GetCollectionPaginatedResponse(
        pagination=PaginationResponse(
            items=0,
            page=1,
            pages=1,
            per_page=1000,
            urls=PaginationResponseUrls(),
        ),
        releases=[],
    )

    try:
        response = get_collection_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("data")

    assert type(response_body) == list
    assert len(response_body) == 0
    assert response.get("statusCode") == 200


@patch(
    "willkronberg.handlers.get_collection_handler.DiscogsService",
    discogs_service_mock,
)
def test_get_collection_handler_success_with_releases(
    lambda_context: lambda_context,
):
    response = None
    error = None

    get_collection_mock.return_value = GetCollectionPaginatedResponse(
        pagination=PaginationResponse(
            items=0,
            page=1,
            pages=1,
            per_page=1000,
            urls=PaginationResponseUrls(),
        ),
        releases=[
            ReleaseInstance.model_validate(
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
            )
        ],
    )

    try:
        response = get_collection_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("data")

    assert type(response_body) == list
    assert len(response_body) == 1
    assert response.get("statusCode") == 200


@patch(
    "willkronberg.handlers.get_collection_handler.DiscogsService",
    discogs_service_mock,
)
def test_get_collection_handler_error(lambda_context: lambda_context):
    response = None
    error = None

    get_collection_mock.side_effect = Exception("test-exception")

    try:
        response = get_collection_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("message")

    assert type(response_body) == str
    assert response_body == "An unexpected error has occurred."
    assert response.get("statusCode") == 500
