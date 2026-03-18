from dataclasses import dataclass
from uuid import UUID, uuid4

from services.auth_service.app.domain.shared.aggregate_root import AggregateRoot


@dataclass(eq=False)
class UserProfile(AggregateRoot):
    # ----------------------------
    # Identity
    # ----------------------------
    id: UUID  # Internal DB primary key
    user_id: UUID  # Supabase user ID
    tenant_id: UUID  # Tenant context

    # ----------------------------
    # Application profile data
    # ----------------------------
    avatar_url: str | None = None
    company_name: str | None = None

    # Geography
    country_code: str = "PE"

    # User-declared, not verified
    phone: str | None = None

    # Onboarding / UX state (Derived flags stored for querying)
    onboarding_completed: bool = False

    # ----------------------------
    # Billing defaults (optional)
    # ----------------------------
    document_type: int | None = None
    document_number: str | None = None

    ruc: str | None = None
    legal_name: str | None = None
    tax_address: str | None = None

    # User-declared (Derived flags stored for querying)
    tax_identity_completed: bool = False

    # -------------------------
    # Factory
    # -------------------------
    @classmethod
    def create(cls, user_id: UUID, tenant_id: UUID) -> "UserProfile":
        profile = cls(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
        )

        profile._recalculate_flags()
        return profile

    # -------------------------
    # Public behavior
    # -------------------------
    def update(
        self,
        *,
        avatar_url: str | None = None,
        company_name: str | None = None,
        country_code: str | None = None,
        phone: str | None = None,
        document_type: int | None = None,
        document_number: str | None = None,
        ruc: str | None = None,
        legal_name: str | None = None,
        tax_address: str | None = None,
    ) -> None:
        """Update profile fields and automatically recalculate derived flags."""

        updates = {
            "avatar_url": avatar_url,
            "company_name": company_name,
            "country_code": country_code,
            "phone": phone,
            "document_type": document_type,
            "document_number": document_number,
            "ruc": ruc,
            "legal_name": legal_name,
            "tax_address": tax_address,
        }

        for field, value in updates.items():
            if value is not None:
                setattr(self, field, value)

        # Always keep invariants consistent
        self._recalculate_flags()

    # -------------------------
    # Internal invariant logic
    # -------------------------
    def _recalculate_flags(self) -> None:
        """Recalculate derived completion flags."""

        # Onboarding completion rule
        self.onboarding_completed = all(
            [
                self.avatar_url,
                self.company_name,
                self.country_code,
                self.phone,
            ]
        )

        # Tax identity completion rule
        self.tax_identity_completed = all(
            [
                self.ruc,
                self.legal_name,
                self.tax_address,
            ]
        )
