import asyncio
import os

from aiogram import Bot, types

from app import config
from app.Consumer import NotifyConsumer


bot = Bot(token=config.TELEGRAM_BOT_API_TOKEN, parse_mode=types.ParseMode.HTML)

queue_connection = None


async def initialize_queue_connection():
    global queue_connection
    from aio_pika import connect_robust

    queue_connection = await connect_robust(
        config.RABBIT_MQ_URL,
    )


def initialize_assets():
    from app.helpers.AssetsHelper import assetsHelper

    assetsHelper.initialize(f'{config.BASEDIR}/assets')


async def run():
    await initialize_queue_connection()
    initialize_assets()

    await NotifyConsumer.receive()


if __name__ == "__main__":
    asyncio.run(run())
