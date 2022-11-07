import json
from typing import Any, Dict

import requests
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from willkronberg.services.blog_service import BlogService
from willkronberg.services.inventory_service import InventoryService

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler(capture_response=False)
@event_source(data_class=APIGatewayProxyEvent)
def get_collection_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Sample pure Lambda function

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
    context: LambdaContext, required

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
    """

    inventory_service = InventoryService()

    data: Dict[str, Any]
    try:
        data = inventory_service.get_inventory()
    except requests.RequestException as e:
        logger.error(e)

        raise e

    return {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": json.dumps({"data": data}),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "authorization,content-type",
            "Content-Type": "application/json",
        },
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler(capture_response=False)
@event_source(data_class=APIGatewayProxyEvent)
def get_articles_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Sample pure Lambda function

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
    context: LambdaContext, required

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
    """

    blog_service = BlogService()

    data: Dict[str, Any]
    try:
        data = blog_service.get_user_articles("will-kronberg")
    except requests.RequestException as e:
        logger.error(e)

        raise e

    return {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": json.dumps({"data": data}),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "authorization,content-type",
            "Content-Type": "application/json",
        },
    }
