from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path


class Settings(BaseSettings):
    REDIS_URL: str
    REDIS_EMIL_URL: str
    SECRET_KEY: str

    ACCESS_KEY_EXPIRE_TIME: int = 3
    REFRESH_KEY_EXPIRE_TIME: int = 10

    REGISTER_URL: str = "http://account_fastapi:8002/account/register"
    LOGIN_URL: str = "http://account_fastapi:8002/account/login"
    LOGIN_OTP_URL: str = "http://account_fastapi:8002/account/login_otp"
    LOGOUT_URL: str = "http://account_fastapi:8002/account/logout"
    EMAIL_URL: str = "http://notification_fastapi:8003/notification/send_notif_email"

    class Config:
        env_file = "/home/mahdi/Documents/rss_project/authorization_fastapi/.env"


settings = Settings()
