from typing import List
from unittest.mock import Mock, patch

import pytest

from willkronberg.services.inventory_service import InventoryService


class Release:
    def __init__(self, artist: str, title: str):
        self.artist = artist
        self.title = title


class CollectionItemInstance:
    def __init__(self, release: Release):
        self.release = release


class CollectionFolder:
    def __init__(self):
        self.releases: CollectionItemInstance = []

    def add_release(self, release: Release):
        self.releases.append(CollectionItemInstance(release))


class User:
    def __init__(self):
        self.collection_folders: List[CollectionFolder] = []

    def add_folder(self, folder: CollectionFolder):
        self.collection_folders.append(folder)

    def reset(self):
        self.collection_folders = []


@pytest.fixture
def discogs_response() -> User:
    return User()


secrets_mock = Mock()
discogs_mock = Mock()


@patch("willkronberg.services.inventory_service.SecretsService", secrets_mock)
@patch("willkronberg.services.inventory_service.Client", discogs_mock)
def test_get_inventory_with_consumer_token_no_folders(discogs_response):
    discogs_mock.return_value.user.return_value = discogs_response

    response = None
    error = None
    try:
        inventory_service = InventoryService()
        response = inventory_service.get_inventory()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert response is not None


@patch("willkronberg.services.inventory_service.SecretsService", secrets_mock)
@patch("willkronberg.services.inventory_service.Client", discogs_mock)
def test_get_inventory_with_consumer_token_with_folders(discogs_response):
    user: User = discogs_response
    folder = CollectionFolder()
    folder.add_release(Release(artist="Chief Keef", title="Finally Rich"))
    user.add_folder(folder)
    discogs_mock.return_value.user.return_value = user

    response = None
    error = None
    try:
        inventory_service = InventoryService()
        response = inventory_service.get_inventory()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert response is not None
