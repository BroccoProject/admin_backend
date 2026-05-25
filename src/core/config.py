from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_ADMIN: str
    SECRET_KEY: str
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"
    
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # Admin Auth Settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Access Requests / Email Settings
    ADMIN_EMAIL: str = "admin@example.com"
    FRONTEND_URL: str = "http://localhost:4200"
    BACKEND_URL: str = "http://localhost:8000"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    model_config = SettingsConfigDict(env_file=[".env", "src/.env"])

settings = Settings()
