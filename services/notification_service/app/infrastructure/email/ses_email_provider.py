import aioboto3
import structlog

from services.notification_service.app.infrastructure.email.email_provider import (
    EmailProvider,
)
from services.notification_service.app.settings import settings

logger = structlog.get_logger(__name__)


class SESEmailProvider(EmailProvider):
    def __init__(self):
        self.region = settings.aws_region
        self.sender_email = settings.email_sender
        self.session = aioboto3.Session()

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> None:

        logger.info(
            "ses_email_provider.send_email",
            recipient=recipient,
            subject=subject,
        )

        async with self.session.client(  # type: ignore
            "ses",
            region_name=self.region,
        ) as ses:
            response = await ses.send_email(
                Source=self.sender_email,
                Destination={
                    "ToAddresses": [recipient],
                },
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Text": {"Data": body},
                    },
                },
            )

            logger.info("ses_email_provider.sent", response=response)

        logger.info(
            "ses_email_provider.email_sent",
            recipient=recipient,
        )
