from datetime import datetime
from unittest.mock import Mock, patch

from atoma.rss import RSSItem

from willkronberg.services.blog_service import BlogService


class GetResponse:
    content = ""

    def raise_for_status(_):
        pass


get_mock = Mock()
parse_rss_bytes_mock = Mock()


@patch("willkronberg.services.blog_service.get", get_mock)
@patch("willkronberg.services.blog_service.parse_rss_bytes", parse_rss_bytes_mock)
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


@patch("willkronberg.services.blog_service.get", get_mock)
@patch("willkronberg.services.blog_service.parse_rss_bytes", parse_rss_bytes_mock)
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


@patch("willkronberg.services.blog_service.get", get_mock)
@patch("willkronberg.services.blog_service.parse_rss_bytes", parse_rss_bytes_mock)
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


@patch("willkronberg.services.blog_service.get", get_mock)
@patch("willkronberg.services.blog_service.parse_rss_bytes", parse_rss_bytes_mock)
def test_get_feed_with_articles_long_description():
    class ParseRSSFeedResponse:
        items = [
            RSSItem(
                guid="test-guid",
                title="test title",
                content_encoded="<p>This is a really really really really really really really really really long description that is definitely over 75 characters in length.</p>",
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
    assert (
        response[0].description
        == "This is a really really really really really really really really really..."
    )
