import json

from unittest.mock import Mock, patch

from willkronberg.handlers.get_articles_handler import get_articles_handler
from willkronberg.models.article import Article
from tests.fixtures.lambda_context import lambda_context

test_article = Article(
    id="test-id",
    title="test-title",
    description="test-description",
    link="https://test-link",
    published_date="2023-09-21",
)

get_articles_mock = Mock()
blog_service_mock = Mock()
blog_service_mock().get_feed = get_articles_mock


@patch("willkronberg.handlers.get_articles_handler.BlogService", blog_service_mock)
def test_get_articles_handler_success(lambda_context: lambda_context):
    response = None
    error = None

    get_articles_mock.return_value = [test_article]

    try:
        response = get_articles_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("data", {})

    assert len(response_body) == 1
    assert type(response_body[0]) == dict
    assert response_body[0].get("id") == "test-id"
    assert response.get("statusCode") == 200


@patch("willkronberg.handlers.get_articles_handler.BlogService", blog_service_mock)
def test_get_articles_handler_failure(lambda_context: lambda_context):
    response = None
    error = None

    get_articles_mock.side_effect = Exception("test-exception")

    try:
        response = get_articles_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {}))

    assert response_body["message"] == "An unexpected error has occurred."
    assert response.get("statusCode") == 500
