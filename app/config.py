import os
from pathlib import Path
from zoneinfo import ZoneInfo

import aiohttp
from dotenv import load_dotenv
from prometheus_client import Counter

load_dotenv()


RABBIT_MQ_URL = os.getenv("RABBIT_MQ_URL", "amqp://guest:guest@localhost/")

TELEGRAM_BOT_API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

TELEGRAM_LOGS_BOT_API_TOKEN = os.getenv("TELEGRAM_LOGS_BOT_API_TOKEN")
TELEGRAM_LOGS_CHAT_ID = os.getenv("TELEGRAM_LOGS_CHAT_ID")

SERVICE_NAME = os.getenv("SERVICE_NAME", "checking")
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs" / SERVICE_NAME

ASSETS_DIR = BASE_DIR / "app" / "assets"

REQUESTS_TIMEOUT = aiohttp.ClientTimeout(total=30)
LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT = os.getenv(
    "LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT",
    "http://127.0.0.1:8000/user/{user_telegram_id}/logout",
)
assert "{user_telegram_id}" in LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT, (
    "LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT must contain {user_telegram_id}"
)

LOGIN_LOGOUT_SERVICE_TOKEN = os.getenv("LOGIN_LOGOUT_SERVICE_TOKEN", "SecretToken")
LOGIN_LOGOUT_SERVICE_HEADER_NAME = os.getenv(
    "LOGIN_LOGOUT_SERVICE_HEADER_NAME", "X-Auth-Token"
)

TIMEZONE = ZoneInfo("Europe/Moscow")


notify_messages_total = Counter(
    "notify_messages_total",
    "Total number of NotifyConsumer messages processed",
    ["message_type", "to_user_telegram_id"],
)
