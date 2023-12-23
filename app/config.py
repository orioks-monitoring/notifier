import logging
import os

from dotenv import load_dotenv


load_dotenv()


RABBIT_MQ_URL = os.getenv("RABBIT_MQ_URL", "amqp://guest:guest@localhost/")

TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

TELEGRAM_LOGS_BOT_API_TOKEN = os.getenv('TELEGRAM_LOGS_BOT_API_TOKEN')
TELEGRAM_LOGS_CHAT_ID = os.getenv('TELEGRAM_LOGS_CHAT_ID')

BASEDIR = os.path.dirname(os.path.abspath(__file__))


LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT = os.getenv(
    'LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT',
    "http://127.0.0.1:8000/user/{user_telegram_id}/logout",
)
assert (
    "{user_telegram_id}" in LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT
), "LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT must contain {user_telegram_id}"

LOGIN_LOGOUT_SERVICE_TOKEN = os.getenv("LOGIN_LOGOUT_SERVICE_TOKEN", "SecretToken")
LOGIN_LOGOUT_SERVICE_HEADER_NAME = os.getenv(
    "LOGIN_LOGOUT_SERVICE_HEADER_NAME", "X-Auth-Token"
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(pathname)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S %d.%m.%Y",
)
