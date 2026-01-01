from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'TemplateApi'
    PROJECT_VERSION: str = '0.0.1'

    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    DATABASE_URL: Optional[str]

    @property
    def full_database_url(self) -> str:
        if self.DATABASE_URL is None:
            return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        return self.DATABASE_URL

    class Config:
        env_file = '.env'


settings = Settings()
