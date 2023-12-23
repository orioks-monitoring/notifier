import asyncio
import logging
from abc import ABC, abstractmethod
from typing import final, NoReturn

from aio_pika.abc import AbstractIncomingMessage

from app import main

logger = logging.getLogger(__name__)


class BaseConsumer(ABC):
    @staticmethod
    @abstractmethod
    async def on_message(message: AbstractIncomingMessage) -> None:
        """Process message."""
        pass

    @property
    @abstractmethod
    def queue_name(self) -> str:
        """Queue name."""
        pass

    @property
    @abstractmethod
    def exceptions_to_requeue(self) -> tuple[Exception, ...]:
        """Exceptions to requeue message."""
        pass

    @classmethod
    @final
    async def receive(cls) -> NoReturn:
        async with main.queue_connection:
            channel = await main.queue_connection.channel()
            queue = await channel.declare_queue(
                cls.queue_name,
                durable=True,
            )
            await channel.set_qos(prefetch_count=1)  # 1 message per second
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process(ignore_processed=True):
                        try:
                            await cls.on_message(message)
                        except cls.exceptions_to_requeue as e:
                            logger.warning("Requeue message, because %s", e)
                            await message.nack(requeue=True)
                        except Exception as e:
                            logger.exception("Error while processing message: %s", e)
                            await message.nack(requeue=False)
                        else:
                            await message.ack()

                        await asyncio.sleep(1)

            logger.info(" [*] Waiting for messages. To exit press CTRL+C")
            try:
                await asyncio.Future()
            finally:
                await main.queue_connection.close()
