from pydantic import BaseModel, SecretStr


class Secret(BaseModel):
    user_token: SecretStr
