from uuid import UUID

from sqlalchemy import select

from services.auth_service.app.domain.user_profiles.models import UserProfile
from services.auth_service.app.domain.user_profiles.repository import (
    UserProfileRepository,
)
from services.auth_service.app.infrastructure.db.models.user_profile import (
    UserProfileModel,
)
from services.auth_service.app.infrastructure.db.repositories.base import (
    SqlAlchemyAggregateRepository,
)


class SqlAlchemyUserProfileRepository(
    SqlAlchemyAggregateRepository[UserProfile, UserProfileModel],
    UserProfileRepository,
):
    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    async def add(self, profile: UserProfile) -> None:
        """
        Persist new aggregate and track it so the UnitOfWork can:
        - collect domain events
        - synchronize domain → ORM before commit
        """
        model = UserProfileModel.from_domain(profile)
        self._session.add(model)

        # Track as NEW aggregate (events only, no sync needed)
        self._track(profile, model)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    async def get_by_user_and_tenant(
        self,
        *,
        user_id: UUID,
        tenant_id: UUID,
    ) -> UserProfile | None:
        """
        Load aggregate and track it with its ORM model
        so it can be synchronized before commit.
        """

        stmt = select(UserProfileModel).where(
            UserProfileModel.user_id == user_id,
            UserProfileModel.tenant_id == tenant_id,
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        domain = model.to_domain()

        # Track LOADED aggregate with ORM model for sync
        self._track(domain, model)

        return domain
