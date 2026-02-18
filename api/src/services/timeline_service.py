from loguru import logger

from src.core.config import Errors
from src.exceptions.timeline import InvalidTimelineNodeError, TimelineNodeNotFoundError, TimelineNotFoundError
from src.models.timeline_nodes import TimelineNode
from src.models.timelines import Timeline
from src.repositories.timeline_repository import TimelineRepository
from src.schemas.integrations.ai.timeline_analysis import AnalysisAction, AnalysisResult
from src.schemas.integrations.github import Commit
from src.schemas.timelines import Timeline as TimelineSchema
from src.schemas.timelines import TimelineCreate, TimelineNodeBase, TimelineNodeCreate, TimelineNodeWithChildren
from src.services.auth_service import TokenData
from src.services.integrations.ai.timeline_analysis_service import TimelineAnalysisService
from src.services.integrations.analysis.activity_clustering_service import ActivityClusteringService


class TimelineService:
    def __init__(
        self,
        timeline_repo: TimelineRepository,
        clustering_service: ActivityClusteringService,
        ai_service: TimelineAnalysisService,
    ) -> None:
        self.timeline_repo = timeline_repo
        self.clustering_service = clustering_service
        self.ai_service = ai_service

    # Timeline Methods
    async def get_user_timelines(self, user_id: int) -> list[Timeline]:
        """Returns the list of timelines (Dashbord View)."""
        return await self.timeline_repo.get_timelines_by_user_id(user_id)

    async def get_timeline_details(self, timeline_id: int, user_id: int) -> TimelineSchema:
        """
        Returns a single timeline with the full Node Tree (Editor View).
        1. Fetch Timeline + All Nodes (Flat)
        2. Sort by Date
        3. Rebuild Tree (Parent -> Children)
        """
        timeline = await self.timeline_repo.get_timeline_with_nodes(timeline_id, user_id)

        if not timeline:
            raise TimelineNotFoundError(Errors.TIMELINE_NOT_FOUND.value)

        # --- TREE CONSTRUCTION LOGIC ---

        # 1. Sort ALL nodes by start_date ASC (so parents and children are both ordered)
        # Note: We sort strictly by start_date. If dates are equal, secondary sort by ID.
        all_nodes = sorted(timeline.nodes, key=lambda n: (n.start_date, n.id))

        # 2. Separate Parents (Blocks) and Children (Spheres)
        # We create a temporary lookup map for parents to easily attach children
        parent_map = {}
        top_level_nodes = []
        orphan_nodes = []  # Fallback for nodes whose parent might have been deleted

        # First pass: Identify potential parents (Top Level Nodes)
        for node in all_nodes:
            node.children = []

            if node.parent_id is None:
                top_level_nodes.append(node)
                parent_map[node.id] = node

        # Second pass: Attach children to their parents
        for node in all_nodes:
            if node.parent_id is not None:
                parent = parent_map.get(node.parent_id)
                if parent:
                    parent.children.append(node)
                else:
                    orphan_nodes.append(node)

        # 3. Overwrite the timeline.nodes list with ONLY the top-level structure
        # The children are now nested inside these objects.
        timeline.nodes = top_level_nodes

        return timeline

    async def create_timeline(self, timeline: TimelineCreate, token_data: TokenData) -> Timeline:
        """Create a new timeline."""
        timeline_db = Timeline(
            title=timeline.title,
            description=timeline.description,
            slug=timeline.slug,
            is_public=timeline.is_public,
            default_zoom_level=timeline.default_zoom_level,
            user_id=token_data.sub,
        )
        return await self.timeline_repo.create_timeline(timeline_db)

    async def delete_timeline(self, timeline_id: int, user_id: int) -> None:
        """Delete a timeline."""
        timeline = await self.timeline_repo.get_timeline_by_id(timeline_id, user_id)
        if not timeline:
            raise TimelineNotFoundError(Errors.TIMELINE_NOT_FOUND.value, details={"timeline_id": timeline_id})

        await self.timeline_repo.delete_timeline(timeline_id)

    # Timeline Node Methods
    async def get_timeline_node_by_id(self, node_id: int) -> TimelineNodeWithChildren:
        """Get a timeline node by ID."""
        node = await self.timeline_repo.get_timeline_node_by_id(node_id)
        if not node:
            raise TimelineNodeNotFoundError(Errors.TIMELINE_NODE_NOT_FOUND.value, details={"node_id": node_id})
        return node

    async def create_timeline_node(self, timeline_node: TimelineNodeCreate, user_id: int) -> TimelineNode:
        """Create a new timeline."""
        timeline = await self.timeline_repo.get_timeline_by_id(timeline_node.timeline_id, user_id)
        if not timeline:
            raise TimelineNotFoundError(
                Errors.TIMELINE_NOT_FOUND.value, details={"timeline_id": timeline_node.timeline_id}
            )

        self._validate_dates(timeline_node)

        if timeline_node.parent_id:
            await self._validate_parent_hierarchy(timeline_node.parent_id, timeline_node, timeline_node.timeline_id)

        timeline_node_db = TimelineNode(
            timeline_id=timeline_node.timeline_id,
            title=timeline_node.title,
            short_summary=timeline_node.short_summary,
            description=timeline_node.description,
            private_notes=timeline_node.private_notes,
            type=timeline_node.type,
            start_date=timeline_node.start_date,
            end_date=timeline_node.end_date,
            is_current=timeline_node.is_current,
            date_granularity=timeline_node.date_granularity,
            github_repo_id=timeline_node.github_repo_id,
            github_pr_id=timeline_node.github_pr_id,
            parent_id=timeline_node.parent_id,
        )

        return await self.timeline_repo.create_timeline_node(timeline_node_db)

    async def update_timeline_node(self, node_id: int, timeline_node: TimelineNodeBase, user_id: int) -> TimelineNode:
        """Update a timeline node."""
        existing_node = await self.get_timeline_node_by_id(node_id)
        timeline = await self.timeline_repo.get_timeline_by_id(existing_node.timeline_id, user_id)
        if not existing_node or not timeline:
            raise TimelineNodeNotFoundError(Errors.TIMELINE_NODE_NOT_FOUND.value, details={"node_id": node_id})

        self._validate_dates(timeline_node)

        if timeline_node.parent_id == node_id:
            raise InvalidTimelineNodeError(
                Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                details={
                    "parent_id": timeline_node.parent_id,
                    "reason": "A node can not be its own parent",
                },
            )

        if timeline_node.parent_id:
            await self._validate_parent_hierarchy(timeline_node.parent_id, timeline_node, existing_node.timeline_id)

        existing_node.title = timeline_node.title
        existing_node.short_summary = timeline_node.short_summary
        existing_node.description = timeline_node.description
        existing_node.private_notes = timeline_node.private_notes
        existing_node.type = timeline_node.type
        existing_node.start_date = timeline_node.start_date
        existing_node.end_date = timeline_node.end_date
        existing_node.is_current = timeline_node.is_current
        existing_node.date_granularity = timeline_node.date_granularity
        existing_node.github_repo_id = timeline_node.github_repo_id
        existing_node.github_pr_id = timeline_node.github_pr_id
        existing_node.parent_id = timeline_node.parent_id

        return await self.timeline_repo.update_timeline_node(node_id, existing_node)

    async def delete_timeline_node(self, node_id: int, user_id: int) -> None:
        """Delete a timeline node"""
        existing_node = await self.timeline_repo.get_timeline_node_lite(node_id)
        if not existing_node:
            raise TimelineNodeNotFoundError(Errors.TIMELINE_NODE_NOT_FOUND.value, details={"node_id": node_id})
        timeline = await self.timeline_repo.get_timeline_by_id(existing_node.timeline_id, user_id)
        if not timeline:
            raise TimelineNodeNotFoundError(Errors.TIMELINE_NODE_NOT_FOUND.value, details={"node_id": node_id})

        await self.timeline_repo.delete_timeline_node(node_id)

    async def generate_nodes_for_commits(
        self, commits: list[Commit], timeline_id: int, repo_id: int, user_id: int
    ) -> None:
        """
        Processes clusters through AI and persists the results as nodes in a specific timeline.
        """

        last_parent: TimelineNode | None = None

        clusters = self.clustering_service.cluster_commits(commits)
        for cluster in clusters:
            if cluster.is_shallow:
                continue
            try:
                ai_result: AnalysisResult = await self.ai_service.analyze_cluster(cluster, repo_id)

                if ai_result.action == AnalysisAction.IGNORE:
                    logger.info(f"AI ignored cluster: {cluster.topic} - Reasoning: {ai_result.reasoning}")
                    continue

                if ai_result.node_content:
                    node_data = TimelineNodeCreate(**ai_result.node_content.model_dump(), timeline_id=timeline_id)
                    node_data.start_date = node_data.start_date.replace(hour=0, minute=0, second=0, microsecond=0)

                    if node_data.end_date is not None:
                        node_data.end_date = node_data.end_date.replace(
                            hour=23, minute=59, second=59, microsecond=999999
                        )

                    node_data.github_repo_id = repo_id
                    if node_data.end_date is not None:
                        node_data.is_current = False

                    if ai_result.action == AnalysisAction.MERGE_TO_PARENT and last_parent:
                        node_data.parent_id = last_parent.id

                        needs_update = False
                        if node_data.start_date < last_parent.start_date:
                            last_parent.start_date = node_data.start_date
                            needs_update = True
                        if node_data.end_date and (
                            not last_parent.end_date or node_data.end_date > last_parent.end_date
                        ):
                            last_parent.end_date = node_data.end_date
                            needs_update = True

                        if needs_update:
                            await self.update_timeline_node(last_parent.id, last_parent, user_id)

                    created_node = await self.create_timeline_node(timeline_node=node_data, user_id=user_id)

                    if last_parent is None or ai_result.action == AnalysisAction.CREATE_NODE:
                        last_parent = created_node

            except Exception as e:
                logger.error(f"Failed to process cluster {cluster.id} for timeline {timeline_id}: {str(e)}")
                continue
        logger.success(f"Timeline generation complete for repository ID: {repo_id}")

    # Helper Validation Methods
    def _validate_dates(self, timeline_node: TimelineNodeCreate | TimelineNodeBase) -> None:
        """Validates the start and end dates based on whether the node is current."""
        is_current = timeline_node.is_current
        start_date = timeline_node.start_date
        end_date = timeline_node.end_date

        if is_current:
            if end_date is not None:
                raise InvalidTimelineNodeError(
                    Errors.INVALID_TIMELINE_NODE.value,
                    details={"reason": "Current nodes must not have an end_date defined"},
                )
        else:
            if start_date and end_date:
                if start_date > end_date:
                    raise InvalidTimelineNodeError(
                        Errors.INVALID_TIMELINE_NODE.value, details={"start_date": start_date, "end_date": end_date}
                    )
            else:
                raise InvalidTimelineNodeError(
                    Errors.INVALID_TIMELINE_NODE.value,
                    details={"reason": "Non-current nodes must have both start_date and end_date defined"},
                )

    async def _validate_parent_hierarchy(
        self, parent_id: int, child_node: TimelineNodeCreate | TimelineNodeBase, timeline_id: int
    ) -> None:
        """Validates relationships between a child node and its requested parent."""

        parent_node = await self.timeline_repo.get_timeline_node_lite(parent_id)
        if not parent_node:
            raise TimelineNodeNotFoundError(Errors.TIMELINE_NODE_NOT_FOUND.value, details={"parent_id": parent_id})

        if parent_node.timeline_id != timeline_id:
            raise InvalidTimelineNodeError(
                Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                details={
                    "parent_id": parent_id,
                    "timeline_id": timeline_id,
                    "reason": "Parent must belong to the same timeline",
                },
            )

        if parent_node.parent_id is not None:
            raise InvalidTimelineNodeError(
                Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                details={"parent_id": parent_id, "reason": "Selected parent is already a child node. Max depth is 2."},
            )

        if not parent_node.start_date:
            raise InvalidTimelineNodeError(
                Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                details={"reason": "Parent node has invalid dates (missing start)"},
            )

        if child_node.start_date < parent_node.start_date:
            raise InvalidTimelineNodeError(
                Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                details={
                    "parent_start_date": parent_node.start_date.isoformat(),
                    "child_start_date": child_node.start_date.isoformat(),
                    "reason": "Child cannot start before parent",
                },
            )

        if not parent_node.is_current:
            if not parent_node.end_date:
                raise InvalidTimelineNodeError(
                    Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                    details={"reason": "Parent node has invalid dates (missing start)"},
                )

            if (child_node.is_current) or (child_node.end_date is None):
                raise InvalidTimelineNodeError(
                    Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                    details={"reason": "Child cannot be 'current' if parent has a fixed end date"},
                )

            if child_node.end_date and child_node.end_date > parent_node.end_date:
                raise InvalidTimelineNodeError(
                    Errors.INVALID_TIMELINE_NODE_HIERARCHY.value,
                    details={
                        "parent_end_date": parent_node.end_date.isoformat(),
                        "child_end_date": child_node.end_date.isoformat(),
                        "reason": "Child cannot end after parent",
                    },
                )
