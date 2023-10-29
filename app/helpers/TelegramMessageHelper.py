from pathlib import Path

from aiogram.types import InputFile

from app import main
# import app.helpers.OrioksHelper as OrioksHelper


class TelegramMessageHelper:
    @staticmethod
    async def text_message_to_user(
        user_telegram_id: int, message: str
    ) -> None:
        # try:
        await main.bot.send_message(user_telegram_id, message)
        # except (BotBlocked, ChatNotFound, UserDeactivated):
        #     OrioksHelper.OrioksHelper.make_orioks_logout(
        #         user_telegram_id=user_telegram_id
        #     )

    @staticmethod
    async def photo_message_to_user(
        user_telegram_id: int, photo_path: str, caption: str
    ) -> None:
        # try:
        await main.bot.send_photo(
            user_telegram_id, InputFile(photo_path), caption
        )
        # except (BotBlocked, ChatNotFound, UserDeactivated):
        #     OrioksHelper.OrioksHelper.make_orioks_logout(
        #         user_telegram_id=user_telegram_id
        #     )
