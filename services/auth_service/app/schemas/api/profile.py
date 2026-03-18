from uuid import UUID

from pydantic import BaseModel

from services.auth_service.app.domain.user_profiles.models import UserProfile


class ProfileUpdateRequest(BaseModel):
    avatar_url: str | None = None
    company_name: str | None = None
    country_code: str | None = None
    phone: str | None = None

    document_type: int | None = None
    document_number: str | None = None

    ruc: str | None = None
    legal_name: str | None = None
    tax_address: str | None = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenant_id: UUID

    avatar_url: str | None
    company_name: str | None
    country_code: str
    phone: str | None

    onboarding_completed: bool

    document_type: int | None
    document_number: str | None

    ruc: str | None
    legal_name: str | None
    tax_address: str | None

    tax_identity_completed: bool

    @classmethod
    def from_domain(cls, profile: UserProfile) -> "ProfileResponse":
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
