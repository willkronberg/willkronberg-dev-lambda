import json

import boto3
from moto import mock_secretsmanager
from mypy_boto3_secretsmanager import SecretsManagerClient

from willkronberg.services.secrets_service import SecretsService


@mock_secretsmanager
def test_get_user_token_success():
    client: SecretsManagerClient = boto3.client("secretsmanager")
    client.create_secret(
        Name="test-secret-name",
        SecretString=json.dumps({"user_token": "test-secret-value"}),
    )

    error = None
    response = None

    try:
        secrets_service = SecretsService()
        response = secrets_service.get_user_token("test-secret-name")
    except Exception as e:
        error = e

    assert error is None
    assert response.get_secret_value() == "test-secret-value"
    assert str(response) == "**********"


@mock_secretsmanager
def test_get_user_token_bad_secret_name():
    error = None
    response = None

    try:
        secrets_service = SecretsService()
        response = secrets_service.get_user_token("not-created-secret")
    except Exception as e:
        error = e

    assert (
        str(error)
        == "An error occurred (ResourceNotFoundException) when calling the GetSecretValue operation: Secrets Manager can't find the specified secret."
    )
    assert response is None
