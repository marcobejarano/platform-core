from aiokafka import AIOKafkaProducer


class RedpandaProducer:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def send(self, topic: str, message: bytes, key: bytes | None = None) -> None:
        if not self._producer:
            raise RuntimeError("Producer not started")

        await self._producer.send_and_wait(topic, message, key=key)
