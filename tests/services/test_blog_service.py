from unittest.mock import Mock, patch
from datetime import datetime

from willkronberg.services.blog_service import BlogService

from atoma.rss import RSSItem


class GetResponse:
    content = ""


get_mock = Mock()
requests_mock = Mock()
requests_mock.get = get_mock


parse_rss_bytes_mock = Mock()
atoma_mock = Mock()
atoma_mock.parse_rss_bytes = parse_rss_bytes_mock


@patch("willkronberg.services.blog_service.requests", requests_mock)
@patch("willkronberg.services.blog_service.atoma", atoma_mock)
def test_get_feed_no_articles():
    class ParseRSSFeedResponse:
        items = []

    get_mock.return_value = GetResponse()
    parse_rss_bytes_mock.return_value = ParseRSSFeedResponse()

    response = None
    error = None

    try:
        blog_service = BlogService()
        response = blog_service.get_feed()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert response == []


@patch("willkronberg.services.blog_service.requests", requests_mock)
@patch("willkronberg.services.blog_service.atoma", atoma_mock)
def test_get_feed_with_articles():
    class ParseRSSFeedResponse:
        items = [
            RSSItem(
                guid="test-guid",
                title="test title",
                content_encoded="<p>test description</p>",
                link="https://test-link.com",
                pub_date=datetime.utcnow(),
                description=None,
                author="Will Kronberg",
                categories=[],
                comments=None,
                enclosures=[],
                source=None,
            )
        ]

    get_mock.return_value = GetResponse()
    parse_rss_bytes_mock.return_value = ParseRSSFeedResponse()

    response = None
    error = None

    try:
        blog_service = BlogService()
        response = blog_service.get_feed()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert len(response) == 1
    assert response[0].id == "test-guid"
    assert response[0].title == "test title"
    assert type(response[0].published_date) == str


@patch("willkronberg.services.blog_service.requests", requests_mock)
@patch("willkronberg.services.blog_service.atoma", atoma_mock)
def test_get_feed_with_articles_bad_id():
    class ParseRSSFeedResponse:
        items = [
            RSSItem(
                guid=1,
                title="test title",
                content_encoded="<p>test description</p>",
                link="https://test-link.com",
                pub_date=datetime.utcnow(),
                description=None,
                author="Will Kronberg",
                categories=[],
                comments=None,
                enclosures=[],
                source=None,
            )
        ]

    get_mock.return_value = GetResponse()
    parse_rss_bytes_mock.return_value = ParseRSSFeedResponse()

    response = None
    error = None

    try:
        blog_service = BlogService()
        response = blog_service.get_feed()
    except Exception as e:
        print(e)
        error = e
        raise e

    assert error is None
    assert len(response) == 1
    assert type(response[0].id) == str
    assert response[0].id == "1"
