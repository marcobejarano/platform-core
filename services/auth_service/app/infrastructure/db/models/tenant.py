from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from services.auth_service.app.domain.tenants.models import (
    Plan,
)
from services.auth_service.app.domain.tenants.models import (
    Tenant as DomainTenant,
)
from services.auth_service.app.infrastructure.db.base import (
    BaseModel,
    TimestampMixin,
)


class TenantModel(BaseModel, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Projection from billing service events
    plan: Mapped[Plan] = mapped_column(
        Enum(Plan, name="tenant_plan"),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    # -------------------------------------------------
    # Mapping helpers
    # -------------------------------------------------

    @classmethod
    def from_domain(cls, tenant: DomainTenant) -> "TenantModel":
        return cls(
            id=tenant.id,
            name=tenant.name,
            plan=tenant.plan,
            is_active=tenant.is_active,
        )

    def update_from_domain(self, tenant: DomainTenant) -> None:
        """
        Synchronize persistence model with aggregate state.
        No business logic here.
        """
        self.name = tenant.name
        self.plan = tenant.plan
        self.is_active = tenant.is_active

    def to_domain(self) -> DomainTenant:
        return DomainTenant(
            id=self.id,
            name=self.name,
            plan=self.plan,
            is_active=self.is_active,
        )
