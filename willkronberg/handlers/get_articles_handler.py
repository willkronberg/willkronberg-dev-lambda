from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from willkronberg.helpers import response_helpers
from willkronberg.services.blog_service import BlogService

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@event_source(data_class=APIGatewayProxyEvent)
def get_articles_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Returns a list of articles from my blog.

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
    context: LambdaContext, required

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
    """

    try:
        blog_service = BlogService()
        articles = blog_service.get_feed()
        deserialized_articles = [article.model_dump() for article in articles]

        return response_helpers.generate_success_response(deserialized_articles)
    except Exception as e:
        logger.exception(e, stack_info=True)

        return response_helpers.generate_error_response(
            500, "An unexpected error has occurred."
        )
