import os

from dotenv import load_dotenv

load_dotenv(".env")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB_NAME = os.environ.get("POSTGRES_DB_NAME")
SQL_LOG = os.environ.get("SQL_LOG", "False")

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecretkey_change_in_production")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

EMAIL_REQUEST_TIMEOUT_SECONDS = int(os.environ.get("EMAIL_REQUEST_TIMEOUT_SECONDS", "30"))
EMAIL_MAX_RETRIES = int(os.environ.get("EMAIL_MAX_RETRIES", "3"))
EMAIL_RETRY_BACKOFF_SECONDS = float(os.environ.get("EMAIL_RETRY_BACKOFF_SECONDS", "1.0"))

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_FROM_EMAIL = os.environ.get("BREVO_FROM_EMAIL", "noreply@example.com")
BREVO_FROM_NAME = os.environ.get("BREVO_FROM_NAME", "Application")
BREVO_REPLY_TO_EMAIL = os.environ.get("BREVO_REPLY_TO_EMAIL", "")
BREVO_REPLY_TO_NAME = os.environ.get("BREVO_REPLY_TO_NAME", "")
OTP_EXPIRE_MINUTES = int(os.environ.get("OTP_EXPIRE_MINUTES", "15"))

# AI Extraction
AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")
AI_MODEL = os.environ.get("AI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
AI_API_URL = os.environ.get("AI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models")
AI_REQUEST_TIMEOUT = int(os.environ.get("AI_REQUEST_TIMEOUT", "180"))
