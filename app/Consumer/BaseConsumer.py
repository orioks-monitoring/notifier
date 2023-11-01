import asyncio
from abc import ABC, abstractmethod
from typing import final

from aio_pika.abc import AbstractIncomingMessage

from app import main


class BaseConsumer(ABC):
    @staticmethod
    @abstractmethod
    async def on_message(message: AbstractIncomingMessage) -> None:
        pass

    @property
    @abstractmethod
    def queue_name(self) -> str:
        pass

    @classmethod
    @final
    async def receive(cls) -> None:
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
                        except Exception as e:
                            print(f"Exception: {e}")
                            await message.nack(requeue=True)
                            await asyncio.sleep(1)
                            continue

            print(" [*] Waiting for messages. To exit press CTRL+C")
            try:
                await asyncio.Future()
            finally:
                await main.queue_connection.close()
