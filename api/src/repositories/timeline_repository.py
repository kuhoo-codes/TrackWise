from loguru import logger
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.timeline_nodes import TimelineNode
from src.models.timelines import Timeline
from src.schemas.timelines import TimelineBase


class TimelineRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # Timeline Methods
    async def get_timeline_by_id(self, timeline_id: int, user_id: int) -> Timeline | None:
        """Retrieve a timeline by its ID."""
        statement = select(Timeline).filter(Timeline.id == timeline_id, Timeline.user_id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_timeline_with_nodes(self, timeline_id: int, user_id: int) -> Timeline | None:
        """
        Get A SINGLE timeline with ALL its nodes loaded.
        Crucial: We verify user_id here to ensure ownership.
        """
        statement = (
            select(Timeline)
            .where(Timeline.id == timeline_id, Timeline.user_id == user_id)
            .options(selectinload(Timeline.nodes).selectinload(TimelineNode.children))
        )
        result = await self.db.execute(statement)
        return result.scalars().first()

    async def get_timelines_by_user_id(self, user_id: int) -> list[Timeline]:
        """
        Get ALL timelines for a user.
        """
        statement = select(Timeline).where(Timeline.user_id == user_id).order_by(Timeline.updated_at.desc())
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def create_timeline(self, timeline: Timeline) -> Timeline:
        """Create a new timeline in the database."""
        self.db.add(timeline)
        await self.db.commit()

        stmt = select(Timeline).options(selectinload(Timeline.nodes)).where(Timeline.id == timeline.id)

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete_timeline(self, timeline_id: int) -> None:
        """Delete a timeline by its ID."""
        stmt = delete(Timeline).where(Timeline.id == timeline_id)
        await self.db.execute(stmt)
        await self.db.commit()

    # Timeline Node Methods
    async def get_timeline_node_lite(self, node_id: int) -> TimelineNode | None:
        """Retrieve a timeline node by its ID."""
        logger.info(f"Fetching timeline node lite for node_id: {node_id}")
        statement = select(TimelineNode).filter(TimelineNode.id == node_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_timeline_node_by_id(self, node_id: int) -> TimelineNode | None:
        """Retrieve a timeline node by its ID, including its children."""
        statement = (
            select(TimelineNode)
            .where(TimelineNode.id == node_id)
            .options(selectinload(TimelineNode.children).selectinload(TimelineNode.children))
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create_timeline_node(self, timeline_node: TimelineNode) -> TimelineNode:
        """Create a new timeline node in the database."""
        self.db.add(timeline_node)
        await self.db.commit()
        stmt = (
            select(TimelineNode).options(selectinload(TimelineNode.children)).where(TimelineNode.id == timeline_node.id)
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_timeline_node(self, node_id: int, timelineNode: TimelineBase) -> TimelineNode:
        """
        Explicitly update specific columns using the Pydantic model.
        Uses exclude_unset=True logic via the service or handles Nones here.
        """

        values_to_update = {
            "title": timelineNode.title,
            "short_summary": timelineNode.short_summary,
            "description": timelineNode.description,
            "private_notes": timelineNode.private_notes,
            "type": timelineNode.type,
            "start_date": timelineNode.start_date,
            "end_date": timelineNode.end_date,
            "is_current": timelineNode.is_current,
            "date_granularity": timelineNode.date_granularity,
            "github_repo_id": timelineNode.github_repo_id,
            "github_pr_id": timelineNode.github_pr_id,
            "parent_id": timelineNode.parent_id,
        }

        clean_values = {k: v for k, v in values_to_update.items() if v is not None}

        if not clean_values:
            # Nothing to update
            return await self.get_timeline_node_lite(node_id)

        stmt = (
            update(TimelineNode)
            .where(TimelineNode.id == node_id)
            .values(**clean_values)
            .execution_options(synchronize_session="fetch")
        )

        await self.db.execute(stmt)
        await self.db.commit()

        result = await self.db.execute(select(TimelineNode).where(TimelineNode.id == node_id))
        return result.scalars().first()

    async def delete_timeline_node(self, node_id: int) -> bool:
        """
        Delete a timeline node AND its children (Cascade Delete).
        """
        delete_children_stmt = delete(TimelineNode).where(TimelineNode.parent_id == node_id)
        await self.db.execute(delete_children_stmt)

        delete_parent_stmt = delete(TimelineNode).where(TimelineNode.id == node_id)
        result = await self.db.execute(delete_parent_stmt)
        await self.db.commit()
        return result.rowcount > 0
