from uuid import UUID

from sqlalchemy import (
    Boolean,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from services.auth_service.app.domain.user_profiles.models import (
    UserProfile as DomainProfile,
)
from services.auth_service.app.infrastructure.db.base import (
    BaseModel,
    TimestampMixin,
)


class UserProfileModel(BaseModel, TimestampMixin):
    __tablename__ = "user_profiles"

    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_profile_user_tenant"),
    )

    # Supabase auth.users.id
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ----------------------------
    # Application profile data
    # ----------------------------

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    company_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # User-declared, not verified
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Geography (SOURCE OF TRUTH)
    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="PE",
        index=True,
    )

    # Onboarding / UX state
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # ----------------------------
    # Billing defaults (optional)
    # Not fiscal truth — user-editable defaults
    # ----------------------------

    # 1=DNI, 4=CE, 7=PASAPORTE
    # Boleta de Venta (B2C – natural person) optional
    document_type: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    # Boleta de Venta (B2C – natural person) optional
    document_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Factura (B2B – company / RUC holder) required
    ruc: Mapped[str | None] = mapped_column(
        String(11),
        nullable=True,
    )

    # Factura (B2B – company / RUC holder) required
    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Factura (B2B – company / RUC holder) required
    tax_address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Indicates whether the user has completed all required tax fields.
    # Data is user-declared and NOT verified with SUNAT.
    tax_identity_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # -----------------------------
    # Mapping helpers
    # -----------------------------
    @classmethod
    def from_domain(cls, profile: DomainProfile) -> "UserProfileModel":
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            tenant_id=profile.tenant_id,
            avatar_url=profile.avatar_url,
            company_name=profile.company_name,
            country_code=profile.country_code,
            phone=profile.phone,
            onboarding_completed=profile.onboarding_completed,
            document_type=profile.document_type,
            document_number=profile.document_number,
            ruc=profile.ruc,
            legal_name=profile.legal_name,
            tax_address=profile.tax_address,
            tax_identity_completed=profile.tax_identity_completed,
        )

    def update_from_domain(self, profile: DomainProfile) -> None:
        self.avatar_url = profile.avatar_url
        self.company_name = profile.company_name
        self.country_code = profile.country_code
        self.phone = profile.phone
        self.onboarding_completed = profile.onboarding_completed
        self.document_type = profile.document_type
        self.document_number = profile.document_number
        self.ruc = profile.ruc
        self.legal_name = profile.legal_name
        self.tax_address = profile.tax_address
        self.tax_identity_completed = profile.tax_identity_completed

    def to_domain(self) -> DomainProfile:
        return DomainProfile(
            id=self.id,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            avatar_url=self.avatar_url,
            company_name=self.company_name,
            country_code=self.country_code,
            phone=self.phone,
            onboarding_completed=self.onboarding_completed,
            document_type=self.document_type,
            document_number=self.document_number,
            ruc=self.ruc,
            legal_name=self.legal_name,
            tax_address=self.tax_address,
            tax_identity_completed=self.tax_identity_completed,
        )
