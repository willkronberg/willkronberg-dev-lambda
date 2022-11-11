import pytest

from willkronberg.services.blog_service import BlogService


def test_get_feed():
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
    assert response is None
