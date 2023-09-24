import pytest

from willkronberg.models.article import Article


@pytest.fixture(autouse=True)
def test_article():
    return Article(
        id="test-id",
        title="test-title",
        description="test-description",
        link="https://test-link",
        published_date="2023-09-21",
    )
