from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    react_app_api_base: str
    google_api_key: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REACT_APP_GOOGLE_MAPS_API_KEY: str
    HF_riddle_bot:str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Build full SQLAlchemy connection URL from parts."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

@lru_cache()
def get_settings():
    return Settings()
