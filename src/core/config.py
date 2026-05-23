from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"

    model_config = SettingsConfigDict(env_file=[".env", "src/.env"])

settings = Settings()
