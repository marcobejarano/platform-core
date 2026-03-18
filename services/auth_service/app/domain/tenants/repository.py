from abc import ABC, abstractmethod
from uuid import UUID

from services.auth_service.app.domain.tenants.models import (
    Tenant,
)


class TenantRepository(ABC):
    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    @abstractmethod
    async def add(self, tenant: Tenant) -> None:
        """Persist a new tenant."""
        ...

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    @abstractmethod
    async def get(self, tenant_id: UUID) -> Tenant | None: ...

    @abstractmethod
    async def exists(self, tenant_id: UUID) -> bool: ...
