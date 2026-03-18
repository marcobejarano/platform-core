from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from services.auth_service.app.domain.shared.aggregate_root import AggregateRoot


class Plan(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass(eq=False)
class Tenant(AggregateRoot):
    id: UUID
    name: str
    plan: Plan  # Projection from billing service
    is_active: bool = True

    # -------------------------------------------------
    # Factory
    # -------------------------------------------------

    @classmethod
    def create(cls, *, name: str) -> "Tenant":
        cleaned_name = name.strip()

        if not cleaned_name:
            raise ValueError("Tenant name cannot be empty")

        tenant = cls(
            id=uuid4(),
            name=cleaned_name,
            plan=Plan.FREE,
            is_active=True,
        )

        # Optional
        # tenant._add_event(TenantCreated(tenant.id))

        return tenant

    # -------------------------------------------------
    # Domain Mutations
    # -------------------------------------------------

    def update_plan(self, plan: Plan) -> None:
        if self.plan == plan:
            return

        self.plan = plan  # Projection update only

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    def deactivate(self) -> None:
        if not self.is_active:
            return

        self.is_active = False

        # Optional
        # self._add_event(TenantDeactivated(self.id))
