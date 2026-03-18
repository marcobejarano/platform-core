from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service.app.application.services.complete_profile_service import (
    CompleteProfileService,
)
from services.auth_service.app.application.services.onboarding_service import (
    OnboardingService,
)
from services.auth_service.app.application.services.tenant_invitation_service import (
    TenantInvitationService,
)
from services.auth_service.app.application.services.tenant_membership_service import (
    TenantMembershipService,
)
from services.auth_service.app.application.services.tenant_service import TenantService
from services.auth_service.app.application.services.user_profile_service import (
    UserProfileService,
)
from services.auth_service.app.domain.auth.models import AuthenticatedUser
from services.auth_service.app.infrastructure.db.session import get_db
from services.auth_service.app.infrastructure.db.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from services.auth_service.app.infrastructure.security.invitation_token import (
    InvitationTokenService,
)
from services.auth_service.app.infrastructure.supabase.auth_service import (
    SupabaseAuthService,
)
from services.auth_service.app.settings import settings


def get_uow(
    db: AsyncSession = Depends(get_db),
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(db)


def get_auth_service() -> SupabaseAuthService:
    return SupabaseAuthService()


def get_current_user(request: Request) -> AuthenticatedUser:
    return request.state.user


def get_user_profile_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> UserProfileService:
    return UserProfileService(uow)


def get_tenant_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TenantService:
    return TenantService(uow)


def get_tenant_membership_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TenantMembershipService:
    return TenantMembershipService(uow)


def get_onboarding_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> OnboardingService:
    return OnboardingService(uow)


def get_complete_profile_service(
    profile_service: UserProfileService = Depends(get_user_profile_service),
    auth_service: SupabaseAuthService = Depends(get_auth_service),
) -> CompleteProfileService:
    return CompleteProfileService(
        profile_service=profile_service,
        auth_service=auth_service,
    )


def get_tenant_invitation_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TenantInvitationService:
    return TenantInvitationService(uow)


def get_invitation_token_service() -> InvitationTokenService:
    return InvitationTokenService(
        secret_key=settings.auth_service_tenant_invitation_secret_key.get_secret_value()
    )


# async def get_producer(request: Request) -> AIOKafkaProducer:
#     producer = getattr(request.app.state, "producer", None)

#     if producer is None:
#         raise RuntimeError("Kafka producer not initialized")

#     return producer

# async def get_event_bus(
#     producer: AIOKafkaProducer = Depends(get_producer),
# ) -> EventBus:
#     return RedpandaEventBus(producer)

# def get_tenant_invitation_service(
#     db: AsyncSession = Depends(get_db),
#     membership_service: TenantMembershipService = Depends(
#         get_tenant_membership_service
#     ),
#     profile_service: UserProfileService = Depends(get_user_profile_service),
#     event_bus: EventBus = Depends(get_event_bus),
# ) -> TenantInvitationService:

#     invitations_repo = SqlAlchemyTenantInvitationRepository(db)

#     return TenantInvitationService(
#         invitations=invitations_repo,
#         memberships=membership_service,
#         profiles=profile_service,
#         event_bus=event_bus,
#     )
