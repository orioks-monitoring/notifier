import html
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO

from aiogram.types import InputFile
from aiogram.utils import markdown
from aiogram.utils.exceptions import (
    Unauthorized,
)

from app import config, main
from app.config import TIMEZONE
from app.helpers.LoginLogoutHelper import LoginLogoutHelper

logger = logging.getLogger(__name__)


@asynccontextmanager
async def make_logout_on_unauthorized(user_telegram_id: int):
    try:
        yield
    except Unauthorized as exception:
        logger.error(
            "Can't send message to user, trying to logout. Exception: %s", exception
        )
        await LoginLogoutHelper.make_logout(user_telegram_id)


class TelegramMessageHelper:
    @staticmethod
    async def text_message_to_user(user_telegram_id: int, message: str) -> None:
        async with make_logout_on_unauthorized(user_telegram_id):
            await main.bot.send_message(user_telegram_id, message)

    @staticmethod
    async def photo_message_to_user(
        user_telegram_id: int, image: BytesIO, caption: str
    ) -> None:
        async with make_logout_on_unauthorized(user_telegram_id):
            await main.bot.send_photo(user_telegram_id, InputFile(image), caption)

    @staticmethod
    async def message_to_admins(message: str, timestamp: datetime) -> None:
        message_without_html = html.escape(message)
        timestamp = timestamp.astimezone(TIMEZONE)

        await main.logs_bot.send_message(
            config.TELEGRAM_LOGS_CHAT_ID,
            markdown.text(
                markdown.text(
                    markdown.hbold("[ADMIN]"),
                    markdown.text(message_without_html),
                    sep=": ",
                ),
                markdown.hitalic(timestamp.strftime("%d.%m.%Y %H:%M:%S")),
                sep="\n",
            ),
        )
