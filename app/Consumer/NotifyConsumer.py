import logging
from typing import Union, Never, NoReturn

import msgpack
from aio_pika.abc import AbstractIncomingMessage
from aiogram.utils.exceptions import (
    RetryAfter,
    RestartingTelegram,
    NetworkError,
    Throttled,
)
from pydantic import TypeAdapter, Field
from typing_extensions import Annotated

from app.Consumer.BaseConsumer import BaseConsumer
from app.helpers.MarksPictureHelper import MarksPictureHelper
from app.helpers.TelegramMessageHelper import TelegramMessageHelper
from message_models.models import (
    MarkChangeMessage,
    HomeworkChangeMessage,
    RequestChangeMessage,
    NewChangeMessage,
    ToAdminsMessage,
)


logger = logging.getLogger(__name__)

Messages = Annotated[
    Union[
        MarkChangeMessage,
        HomeworkChangeMessage,
        RequestChangeMessage,
        NewChangeMessage,
        ToAdminsMessage,
    ],
    Field(discriminator='type'),
]


def assert_never(_: Never) -> NoReturn:
    raise AssertionError("Unhandled type")


class NotifyConsumer(BaseConsumer):
    queue_name = "notifier"
    exceptions_to_requeue = (
        RetryAfter,
        RestartingTelegram,
        NetworkError,
        Throttled,
    )

    @staticmethod
    async def on_message(message: AbstractIncomingMessage) -> None:
        data = msgpack.unpackb(message.body, raw=False)
        type_adapter = TypeAdapter(Messages)
        message_model = type_adapter.validate_python(data)

        print(f" [x] Received message {message!r}")
        print(f"{message_model=}")

        match message_model:
            case MarkChangeMessage():
                async with MarksPictureHelper() as helper:
                    image_path = helper.get_image_marks(
                        current_grade=message_model.current_grade,
                        max_grade=message_model.max_grade,
                        title_text=message_model.title_text,
                        mark_change_text=message_model.mark_change_text,
                        side_text=message_model.side_text,
                    )
                    await TelegramMessageHelper.photo_message_to_user(
                        user_telegram_id=message_model.user_telegram_id,
                        photo_path=image_path,
                        caption=message_model.caption,
                    )
            case HomeworkChangeMessage():
                await TelegramMessageHelper.text_message_to_user(
                    user_telegram_id=message_model.user_telegram_id,
                    message=message_model.message,
                )
            case RequestChangeMessage():
                await TelegramMessageHelper.text_message_to_user(
                    user_telegram_id=message_model.user_telegram_id,
                    message=message_model.message,
                )
            case NewChangeMessage():
                async with MarksPictureHelper() as helper:
                    image_path = helper.get_image_news(
                        title_text=message_model.title_text,
                        side_text=message_model.side_text,
                        url=message_model.url,
                    )
                    await TelegramMessageHelper.photo_message_to_user(
                        user_telegram_id=message_model.user_telegram_id,
                        photo_path=image_path,
                        caption=message_model.caption,
                    )
            case ToAdminsMessage():
                await TelegramMessageHelper.message_to_admins(
                    message=message_model.message
                )
            case _ as unreadable:
                assert_never(unreadable)
