import os

from dotenv import load_dotenv


load_dotenv()


RABBIT_MQ_URL = os.getenv("RABBIT_MQ_URL", "amqp://guest:guest@localhost/")
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
BASEDIR = os.path.dirname(os.path.abspath(__file__))
