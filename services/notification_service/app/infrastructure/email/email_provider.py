import structlog

logger = structlog.get_logger(__name__)


class EmailProvider:
    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> None:
        pass
