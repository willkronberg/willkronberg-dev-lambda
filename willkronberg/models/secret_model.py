from pydantic import BaseModel, SecretStr


class SecretModel(BaseModel):
    user_token: SecretStr
