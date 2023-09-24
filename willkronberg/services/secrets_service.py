import boto3
from aws_lambda_powertools import Logger
from mypy_boto3_secretsmanager import SecretsManagerClient
from pydantic import SecretStr

from willkronberg.models.secret import Secret

logger = Logger(__name__)


class SecretsService:
    """Service for interacting with AWS SecretsManager"""

    __client__: SecretsManagerClient

    def __init__(self):
        """Creates an instance of the SecretsService"""

        self.__client__ = boto3.client(
            service_name="secretsmanager",
            region_name="us-east-1",
        )

    def get_user_token(self, secret_name: str) -> SecretStr:
        """Retrieves the user token from the AWS SecretsManager secret.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            SecretStr: A secure object that contains the user token.
        """
        return self.__get_secret_value__(secret_name).user_token

    def __get_secret_value__(self, secret_name: str) -> Secret:
        """Retrieves the value of the provided secret.

        Args:
            secret_name (str): The name of the AWS SecretsManager secret to retrieve.

        Returns:
            SecretModel: A validated and secure secret object.
        """
        return Secret.model_validate_json(
            self.__client__.get_secret_value(SecretId=secret_name)["SecretString"]
        )
