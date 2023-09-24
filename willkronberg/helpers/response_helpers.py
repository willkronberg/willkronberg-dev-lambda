import json
from typing import Any, Dict


def generate_success_response(data: Any) -> Dict[str, Any]:
    """Returns a successful response for the AWS Lambda runtime environment.

    Args:
        data (Any): The data to return to the requester.

    Returns:
        Dict[str, Any]: The AWS Lambda response.
    """
    return generate_response(200, {"data": data})


def generate_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Returns an error response for the AWS Lambda runtime environment.

    Args:
        status_code (int): The status code to return to the requester.
        message (str): The error message to return to the requester.

    Returns:
        Dict[str, Any]: The AWS Lambda response.
    """
    return generate_response(status_code, {"message": message})


def generate_response(status_code: int, body: Any) -> Dict[str, Any]:
    """Returns a response for the AWS Lambda runtime environment.

    Args:
        status_code (int): The status code to return to the requester.
        body (Any): The response body to return to the requester.

    Returns:
        Dict[str, Any]: The AWS Lambda response.
    """
    return {
        "statusCode": status_code,
        "isBase64Encoded": False,
        "body": json.dumps(body),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Headers": "authorization,content-type",
            "Content-Type": "application/json",
        },
    }
