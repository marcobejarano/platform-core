import structlog

from services.notification_service.app.application.templates.template_renderer import (
    TemplateRenderer,
)
from services.notification_service.app.infrastructure.email.email_provider import (
    EmailProvider,
)
from services.notification_service.app.schemas.email_event import (
    TenantInvitationCreatedEvent,
)

logger = structlog.get_logger(__name__)


class EmailService:
    def __init__(
        self,
        provider: EmailProvider,
        renderer: TemplateRenderer,
    ):
        self.provider = provider
        self.renderer = renderer

    async def handle_tenant_invitation_created(
        self,
        event: TenantInvitationCreatedEvent,
    ) -> None:

        logger.info(
            "email_service.invitation_received",
            invitation_id=str(event.invitation_id),
            email=event.email,
        )

        invitation_link = f"https://app.example.com/invitations/{event.invitation_id}"

        subject = "You have been invited to join a tenant"

        body = self.renderer.render(
            "invitation_email.txt",
            role=event.role,
            invitation_link=invitation_link,
        )

        await self.provider.send_email(
            recipient=event.email,
            subject=subject,
            body=body,
        )

        logger.info(
            "email_service.invitation_email_sent",
            email=event.email,
        )
