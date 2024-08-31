import logging
from typing import Never, NoReturn, Union

import msgpack
from aio_pika.abc import AbstractIncomingMessage
from aiogram.utils.exceptions import (
    NetworkError,
    RestartingTelegram,
    RetryAfter,
    Throttled,
)
from pydantic import Field, TypeAdapter
from typing_extensions import Annotated

from app.config import notify_messages_total
from app.Consumer.BaseConsumer import BaseConsumer
from app.helpers.MarksPictureHelper import MarksPictureHelper
from app.helpers.TelegramMessageHelper import TelegramMessageHelper
from message_models.models import (
    HomeworkChangeMessage,
    MarkChangeMessage,
    NewChangeMessage,
    RequestChangeMessage,
    ToAdminsMessage,
)

logger = logging.getLogger(__name__)

Message = Annotated[
    Union[
        MarkChangeMessage,
        HomeworkChangeMessage,
        RequestChangeMessage,
        NewChangeMessage,
        ToAdminsMessage,
    ],
    Field(discriminator="type"),
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
        type_adapter = TypeAdapter(Message)
        message_model = type_adapter.validate_python(data)

        logger.info(f"[x] Received message {message!r}, {message_model=}")

        match message_model:
            case MarkChangeMessage():
                notify_messages_total.labels(
                    message_type="MarkChange",
                    to_user_telegram_id=str(message_model.user_telegram_id),
                ).inc()
                async with MarksPictureHelper() as helper:
                    image = helper.get_image_marks(
                        current_grade=message_model.current_grade,
                        max_grade=message_model.max_grade,
                        title_text=message_model.title_text,
                        mark_change_text=message_model.mark_change_text,
                        side_text=message_model.side_text,
                    )
                    await TelegramMessageHelper.photo_message_to_user(
                        user_telegram_id=message_model.user_telegram_id,
                        image=image,
                        caption=message_model.caption,
                    )
            case HomeworkChangeMessage():
                notify_messages_total.labels(
                    message_type="HomeworkChange",
                    to_user_telegram_id=str(message_model.user_telegram_id),
                ).inc()
                await TelegramMessageHelper.text_message_to_user(
                    user_telegram_id=message_model.user_telegram_id,
                    message=message_model.message,
                )
            case RequestChangeMessage():
                notify_messages_total.labels(
                    message_type="RequestChange",
                    to_user_telegram_id=str(message_model.user_telegram_id),
                ).inc()
                await TelegramMessageHelper.text_message_to_user(
                    user_telegram_id=message_model.user_telegram_id,
                    message=message_model.message,
                )
            case NewChangeMessage():
                notify_messages_total.labels(
                    message_type="NewChange",
                    to_user_telegram_id=str(message_model.user_telegram_id),
                ).inc()
                async with MarksPictureHelper() as helper:
                    image = helper.get_image_news(
                        title_text=message_model.title_text,
                        side_text=message_model.side_text,
                        url=message_model.url,
                    )
                    await TelegramMessageHelper.photo_message_to_user(
                        user_telegram_id=message_model.user_telegram_id,
                        image=image,
                        caption=message_model.caption,
                    )
            case ToAdminsMessage():
                notify_messages_total.labels(
                    message_type="ToAdmins",
                    to_user_telegram_id="_admins",
                ).inc()
                await TelegramMessageHelper.message_to_admins(
                    message=message_model.message,
                    timestamp=message.timestamp,  # pyright: ignore[reportArgumentType]
                )
            case _ as unreadable:
                assert_never(unreadable)
