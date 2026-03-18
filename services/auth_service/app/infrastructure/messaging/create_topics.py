import asyncio
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError

from services.auth_service.app.settings import settings


TOPICS = [
    NewTopic(
        name="tenant.invitation.events",
        num_partitions=6,
        replication_factor=1,
    ),
]


async def main():
    admin = AIOKafkaAdminClient(
        bootstrap_servers=settings.redpanda_bootstrap_servers
    )

    await admin.start()

    try:
        existing_topics = await admin.list_topics()

        for topic in TOPICS:
            if topic.name in existing_topics:
                print(f"Topic already exists: {topic.name}")
                continue

            try:
                await admin.create_topics([topic])
                print(f"Created topic: {topic.name}")

            except TopicAlreadyExistsError:
                print(f"Topic already exists: {topic.name}")

    finally:
        await admin.close()


if __name__ == "__main__":
    asyncio.run(main())

# Run once:
# python -m services.auth_service.app.infrastructure.messaging.create_topics
