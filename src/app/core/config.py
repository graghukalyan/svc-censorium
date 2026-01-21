"""Configuration management."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "SVC Censorium"
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
