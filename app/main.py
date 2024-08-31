import asyncio
import logging
from typing import NoReturn

from aiogram import Bot, types
from prometheus_client import start_http_server

from app import config
from app.Consumer.NotifyConsumer import NotifyConsumer
from app.logging import setup_logging

logger = logging.getLogger(__name__)

bot = Bot(
    token=config.TELEGRAM_BOT_API_TOKEN,
    parse_mode=types.ParseMode.HTML,
)
logs_bot = Bot(
    token=config.TELEGRAM_LOGS_BOT_API_TOKEN,
    parse_mode=types.ParseMode.HTML,
)

queue_connection = None


async def initialize_queue_connection() -> None:
    global queue_connection
    from aio_pika import connect_robust

    queue_connection = await connect_robust(
        config.RABBIT_MQ_URL,
        client_properties={
            "connection_name": "notifier",
        },
    )


async def run() -> NoReturn:
    setup_logging()
    await initialize_queue_connection()
    logger.info("Starting metrics server...")
    start_http_server(port=8880)
    logger.info("Metrics server started.")

    await NotifyConsumer.receive()


if __name__ == "__main__":
    asyncio.run(run())
