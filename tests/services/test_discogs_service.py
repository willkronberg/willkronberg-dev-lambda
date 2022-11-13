from unittest.mock import Mock, patch
from typing import Any, Dict
from willkronberg.services.discogs_service import DiscogsService
import pytest


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
            "pagination": {"page": 1},
            "releases": [],
        }
    )

    response = None
    error = None

    try:
        discogs_service = DiscogsService()
        response = discogs_service.get_collection()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert response["pagination"]["page"] == 1
    assert len(response["releases"]) == 0


@patch("willkronberg.services.discogs_service.SecretsService", secrets_mock)
@patch("willkronberg.services.discogs_service.requests", requests_mock)
def test_get_collection_no_releases():
    get_mock.return_value = GetResponse(
        data={
            "pagination": {"page": 1},
            "releases": [{id: "test-id"}],
        }
    )

    response = None
    error = None

    try:
        discogs_service = DiscogsService()
        response = discogs_service.get_collection()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert response["pagination"]["page"] == 1
    assert len(response["releases"]) == 1
