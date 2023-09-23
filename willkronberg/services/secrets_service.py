import boto3
from aws_lambda_powertools import Logger
from mypy_boto3_secretsmanager import SecretsManagerClient

from willkronberg.models.secret_model import SecretModel

logger = Logger(__name__)


class SecretsService:
    __client__: SecretsManagerClient

    def __init__(self):
        self.__client__ = boto3.client(
            service_name="secretsmanager",
            region_name="us-east-1",
        )

    def get_user_token(self, secret_name: str) -> str:
        return self.__get_secret_value__(secret_name).user_token.get_secret_value()

    def __get_secret_value__(self, secret_name: str) -> SecretModel:
        return SecretModel.model_validate_json(
            self.__client__.get_secret_value(SecretId=secret_name)["SecretString"]
        )
