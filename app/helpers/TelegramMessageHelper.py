import logging

from aiogram.types import InputFile
from aiogram.utils import markdown
from aiogram.utils.exceptions import (
    BotBlocked,
    ChatNotFound,
    UserDeactivated,
    Unauthorized,
    RestartingTelegram,
)
import aiohttp
from app import main, config
from app.config import (
    LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT,
    LOGIN_LOGOUT_SERVICE_HEADER_NAME,
    LOGIN_LOGOUT_SERVICE_TOKEN,
)


logger = logging.getLogger(__name__)


def make_logout_on_unauthorized_decorator(func: callable) -> callable:
    async def wrapper(*args, **kwargs) -> callable:
        try:
            return await func(*args, **kwargs)
        except Unauthorized as exception:
            logger.error(
                "Can't send message to user, trying to logout. Exception: %s", exception
            )

            async with aiohttp.ClientSession() as http_session:
                logger.info(
                    "Sending logout request to logout service for user %s",
                    kwargs.get('user_telegram_id'),
                )
                url = LOGIN_LOGOUT_SERVICE_URL_FOR_LOGOUT.format(
                    user_telegram_id=kwargs.get('user_telegram_id')
                )
                headers = {
                    LOGIN_LOGOUT_SERVICE_HEADER_NAME: LOGIN_LOGOUT_SERVICE_TOKEN,
                    "User-Agent": 'NotifyService',
                }
                response = await http_session.post(url, headers=headers)
                response.raise_for_status()

    return wrapper


class TelegramMessageHelper:
    @staticmethod
    @make_logout_on_unauthorized_decorator
    async def text_message_to_user(user_telegram_id: int, message: str) -> None:
        await main.bot.send_message(user_telegram_id, message)

    @staticmethod
    @make_logout_on_unauthorized_decorator
    async def photo_message_to_user(
        user_telegram_id: int, photo_path: str, caption: str
    ) -> None:
        await main.bot.send_photo(user_telegram_id, InputFile(photo_path), caption)

    @staticmethod
    async def message_to_admins(message: str) -> None:
        await main.logs_bot.send_message(
            config.TELEGRAM_LOGS_CHAT_ID,
            markdown.text(
                markdown.hbold('[ADMIN]'),
                markdown.text(message),
                sep=': ',
            ),
        )
