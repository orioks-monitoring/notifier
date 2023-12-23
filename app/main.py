import asyncio
from typing import NoReturn

from aiogram import Bot, types

from app import config
from app.Consumer.NotifyConsumer import NotifyConsumer


bot = Bot(token=config.TELEGRAM_BOT_API_TOKEN, parse_mode=types.ParseMode.HTML)
logs_bot = Bot(
    token=config.TELEGRAM_LOGS_BOT_API_TOKEN, parse_mode=types.ParseMode.HTML
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


def initialize_assets() -> None:
    from app.helpers.AssetsHelper import assetsHelper

    assetsHelper.initialize(f'{config.BASEDIR}/assets')


async def run() -> NoReturn:
    await initialize_queue_connection()
    initialize_assets()

    await NotifyConsumer.receive()


if __name__ == "__main__":
    asyncio.run(run())
