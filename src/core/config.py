from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = "api-key-temporary"
    db_file: str = "data.db"


settings = Settings()
