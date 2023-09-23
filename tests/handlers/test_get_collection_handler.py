import json

from unittest.mock import Mock, patch

from willkronberg.handlers.get_collection_handler import get_collection_handler
from tests.fixtures.lambda_context import lambda_context

get_inventory_mock = Mock()
inventory_service_mock = Mock()
inventory_service_mock().get_inventory = get_inventory_mock


@patch(
    "willkronberg.handlers.get_collection_handler.InventoryService",
    inventory_service_mock,
)
def test_get_collection_handler_success(lambda_context: lambda_context):
    response = None
    error = None

    get_inventory_mock.return_value = []

    try:
        response = get_collection_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("data")

    assert type(response_body) == list
    assert len(response_body) == 0
    assert response.get("statusCode") == 200


@patch(
    "willkronberg.handlers.get_collection_handler.InventoryService",
    inventory_service_mock,
)
def test_get_collection_handler_error(lambda_context: lambda_context):
    response = None
    error = None

    get_inventory_mock.side_effect = Exception("test-exception")

    try:
        response = get_collection_handler({}, lambda_context)
    except Exception as e:
        error = e

    assert error is None

    response_body = json.loads(response.get("body", {})).get("message")

    assert type(response_body) == str
    assert response_body == "An unexpected error has occurred."
    assert response.get("statusCode") == 500
