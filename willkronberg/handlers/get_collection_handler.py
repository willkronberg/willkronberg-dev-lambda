import json

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
def get_collection_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    """Retrieves a list of releases from Discogs that I own

    Parameters
    ----------
    event: APIGatewayProxyEvent, required
    context: LambdaContext, required

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict
    """

    try:
        inventory_service = InventoryService()
        data = inventory_service.get_inventory()

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
    except Exception as e:
        logger.error(e)

        return {
            "statusCode": 500,
            "isBase64Encoded": False,
            "body": json.dumps({"message": "An unexpected error has occurred."}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "authorization,content-type",
                "Content-Type": "application/json",
            },
        }
