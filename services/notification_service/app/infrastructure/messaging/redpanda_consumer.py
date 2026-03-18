import json

import structlog
from aiokafka import AIOKafkaConsumer

logger = structlog.get_logger(__name__)


class RedpandaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list[str]):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.consumer: AIOKafkaConsumer | None = None

    async def start(self):

        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode()),
            enable_auto_commit=True,
        )

        await self.consumer.start()

        logger.info(
            "redpanda_consumer.started",
            topics=self.topics,
        )

    async def stop(self):

        if self.consumer:
            await self.consumer.stop()

        logger.info("redpanda_consumer.stopped")

    async def consume(self, handler):

        assert self.consumer is not None

        async for message in self.consumer:
            logger.info(
                "redpanda_consumer.message_received",
                topic=message.topic,
            )

            await handler(message.topic, message.value)
