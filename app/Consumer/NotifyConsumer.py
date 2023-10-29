from typing import Union

import msgpack
from aio_pika.abc import AbstractIncomingMessage
from pydantic import TypeAdapter, Field
from typing_extensions import Annotated

from app.Consumer import BaseConsumer
from app.helpers import MarksPictureHelper, TelegramMessageHelper
from message_models.ChangeMessage import MarkChangeMessage, HomeworkChangeMessage, RequestChangeMessage, NewChangeMessage

ChangeMessages = Annotated[
    Union[
        MarkChangeMessage,
        HomeworkChangeMessage,
        RequestChangeMessage,
        NewChangeMessage,
    ],
    Field(discriminator='type')
]


class NotifyConsumer(BaseConsumer):
    queue_name = "notifier"

    @staticmethod
    async def on_message(message: AbstractIncomingMessage) -> None:

        data = msgpack.unpackb(message.body, raw=False)
        type_adapter = TypeAdapter(ChangeMessages)
        message_model = type_adapter.validate_python(data)

        print(f" [x] Received message {message!r}")
        print(f"{message_model=}")

        if isinstance(message_model, MarkChangeMessage):
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
        elif isinstance(message_model, HomeworkChangeMessage):
            await TelegramMessageHelper.text_message_to_user(
                user_telegram_id=message_model.user_telegram_id,
                message=message_model.message,
            )
        elif isinstance(message_model, RequestChangeMessage):
            await TelegramMessageHelper.text_message_to_user(
                user_telegram_id=message_model.user_telegram_id,
                message=message_model.message,
            )
        elif isinstance(message_model, NewChangeMessage):
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
