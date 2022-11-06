import json
from typing import Dict

import boto3
from aws_lambda_powertools import Logger
from mypy_boto3_secretsmanager import SecretsManagerClient

logger = Logger(__name__)


class SecretsService:
    session: boto3.Session
    client: SecretsManagerClient

    def __init__(self):
        self.session = boto3.Session
        self.client = boto3.client(
            service_name="secretsmanager",
            region_name="us-east-1",
        )

    def get_user_token(self, secret_name: str) -> str:
        return self.get_secret_value(secret_name)["user_token"]

    def get_secret_value(self, secret_name: str) -> Dict[str, str]:
        return json.loads(
            self.client.get_secret_value(SecretId=secret_name)["SecretString"]
        )
