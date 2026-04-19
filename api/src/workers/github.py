from loguru import logger

from src.db.database import SessionLocal
from src.schemas.users import TokenData
from src.services.factory import ServiceFactory


async def github_full_sync_worker(user_id: int, access_token: str) -> None:
    """
    Handles the background sync process.
    Manages its own DB session to avoid GC errors.
    """
    async with SessionLocal() as db:
        try:
            service = ServiceFactory.create_github_service(db)

            # Re-fetch profile to attach it to THIS session
            profile = await service.get_external_profile(user_id=user_id)
            if not profile:
                logger.error(f"Sync failed: Profile not found for user {user_id}")
                return

            await service.run_full_sync(access_token=access_token, github_profile=profile)

        except Exception as e:
            logger.exception(f"Background Sync Worker failed for user {user_id}: {e}")


async def github_timeline_worker(token_data: TokenData, repository_ids: list[int]) -> None:
    """
    Handles background timeline generation.
    """
    async with SessionLocal() as db:
        try:
            service = ServiceFactory.create_github_service(db)
            await service.generate_github_timelines(token_data=token_data, repository_ids=repository_ids)
        except Exception as e:
            logger.exception(f"Background Timeline Worker failed for user {token_data.sub}: {e}")
