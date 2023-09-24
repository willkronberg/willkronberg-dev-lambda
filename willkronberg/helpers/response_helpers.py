import json
from typing import Any


def generate_success_response(data: Any):
    return generate_response(200, {"data": data})


def generate_error_response(status_code: int, message: str):
    return generate_response(status_code, {"message": message})


def generate_response(status_code: int, body: Any):
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
