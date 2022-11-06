import json
from typing import Any, Dict

import requests
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

from willkronberg.services.inventory_service import InventoryService

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler(capture_response=False)
@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Sample pure Lambda function

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: LambdaContext, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
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
