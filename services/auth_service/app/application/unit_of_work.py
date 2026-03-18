from abc import ABC, abstractmethod
from typing import TypeVar

from services.auth_service.app.application.messaging.outbox_repository import (
    OutboxRepository,
)
from services.auth_service.app.domain.tenant_invitations.repository import (
    TenantInvitationRepository,
)
from services.auth_service.app.domain.tenant_memberships.repository import (
    TenantMembershipRepository,
)
from services.auth_service.app.domain.tenants.repository import (
    TenantRepository,
)
from services.auth_service.app.domain.user_profiles.repository import (
    UserProfileRepository,
)

UOW = TypeVar("UOW", bound="UnitOfWork")


class UnitOfWork(ABC):
    """
    Defines a transactional boundary.
    Coordinates repositories inside a single atomic operation.
    """

    # Repositories exposed inside the transactional boundary
    profiles: UserProfileRepository
    tenants: TenantRepository
    memberships: TenantMembershipRepository
    invitations: TenantInvitationRepository
    outbox: OutboxRepository

    # -------------------------
    # Context manager behavior
    # -------------------------

    @abstractmethod
    async def __aenter__(self: UOW) -> UOW:
        """
        Enter transactional scope.
        Repositories must be initialized here.
        """
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        On success -> commit.
        On error   -> rollback.
        """
        raise NotImplementedError

    # -------------------------
    # Transaction control
    # -------------------------

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit the transaction.
        Must include domain-event collection and outbox persistence.
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """
        Roll back the transaction.
        """
        raise NotImplementedError
