from typing import Any
from uuid import UUID


class AuthServiceException(Exception):
    """Base exception for auth service"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AuthServiceException):
    """Resource not found"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class UnauthorizedException(AuthServiceException):
    """Authentication required"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AuthServiceException):
    """Insufficient permissions"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class ValidationException(AuthServiceException):
    """Validation error"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=422, details=details)


class ConflictException(AuthServiceException):
    """Resource conflict (e.g., duplicate)"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=409, details=details)


class SupabaseAuthException(AuthServiceException):
    """Supabase authentication error"""

    def __init__(self, message: str, original_error: Exception | None = None):
        details = {"original_error": str(original_error)} if original_error else {}
        super().__init__(message=message, status_code=401, details=details)


class TenantNotFoundException(NotFoundException):
    def __init__(self, tenant_id: UUID):
        super().__init__(
            resource="Tenant",
            identifier=tenant_id,
        )


class CannotAddMembersToIndividualTenantException(ForbiddenException):
    def __init__(self, tenant_id: UUID):
        super().__init__(message=f"Cannot add members to individual tenant {tenant_id}")


class MembershipAlreadyExistsException(ConflictException):
    def __init__(self, tenant_id: UUID, user_id: UUID):
        super().__init__(
            message="User is already a member of this tenant",
            details={
                "tenant_id": str(tenant_id),
                "user_id": str(user_id),
            },
        )


class OnboardingError(AuthServiceException):
    """Failure during user onboarding/bootstrap"""

    def __init__(
        self,
        message: str = "Failed to bootstrap user",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=500,
            details=details,
        )
