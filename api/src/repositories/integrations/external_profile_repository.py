from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.integrations import ExternalProfile, PlatformEnum, SyncStatusEnum, SyncStepEnum


class ExternalProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_external_profile(self, external_profile: ExternalProfile) -> ExternalProfile:
        """Create a new external profile in the database."""
        self.db.add(external_profile)
        await self.db.commit()
        await self.db.refresh(external_profile)
        return external_profile

    async def get_external_profile_by_user_id(
        self, user_id: Annotated[int, "The user's ID (foreign key)"], platform: PlatformEnum
    ) -> ExternalProfile | None:
        """Fetch an external profile for a given user and platform."""
        statement = select(ExternalProfile).filter(
            ExternalProfile.user_id == user_id and ExternalProfile.platform == platform
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def update_external_profile(self, external_profile: ExternalProfile) -> ExternalProfile:
        """Merge and update an existing external profile in the database."""
        updated = await self.db.merge(external_profile)
        await self.db.commit()
        await self.db.refresh(updated)
        return updated

    async def set_sync_status(
        self,
        profile_id: Annotated[int, "The ID of the external profile being updated"],
        status: SyncStatusEnum,
        error: str | None = None,
    ) -> ExternalProfile:
        """Update sync status, error message, and last attempt timestamp for a profile."""
        stmt = (
            update(ExternalProfile)
            .where(ExternalProfile.id == profile_id)
            .values(sync_status=status, last_sync_error=error, last_sync_attempt_at=datetime.now(timezone.utc))
            .returning(ExternalProfile)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()

    async def set_sync_step(
        self, profile_id: Annotated[int, "The ID of the external profile being updated"], step: SyncStepEnum
    ) -> ExternalProfile:
        """Record the last successfully completed synchronization step."""
        stmt = (
            update(ExternalProfile)
            .where(ExternalProfile.id == profile_id)
            .values(sync_step=step)
            .returning(ExternalProfile)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()
