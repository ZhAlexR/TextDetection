from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    AWS_ACCESS_KEY: str = "default-access-key"
    AWS_SECRET_KEY: str = "default-secret-key"
    AWS_REGION: str = "default-aws-region"
    OPENAI_API_KEY: str = "default-openai-key"
    BOT_TOKEN: str = "default-bot-token"


settings = Settings()
