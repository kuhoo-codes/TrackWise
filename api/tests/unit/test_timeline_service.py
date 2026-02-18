from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.exceptions.timeline import (
    InvalidTimelineNodeError,
    TimelineNotFoundError,
)
from src.models.timeline_nodes import TimelineNode
from src.models.timelines import Timeline
from src.schemas.integrations.ai.timeline_analysis import AnalysisAction, AnalysisResult
from src.schemas.integrations.analysis.cluster import Cluster
from src.schemas.timelines import TimelineCreate, TimelineNodeBase, TimelineNodeCreate
from src.services.auth_service import TokenData
from src.services.timeline_service import TimelineService


@pytest.fixture
def mock_timeline_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_clustering_service() -> MagicMock:
    """Fixture for a mocked ActivityClusteringService."""
    return MagicMock()


@pytest.fixture
def mock_ai_service() -> AsyncMock:
    """Fixture for a mocked TimelineAnalysisService."""
    return AsyncMock()


@pytest.fixture
def timeline_service(
    mock_timeline_repo: AsyncMock, mock_clustering_service: MagicMock, mock_ai_service: AsyncMock
) -> TimelineService:
    """Fixture for TimelineService with all required dependencies."""
    return TimelineService(
        timeline_repo=mock_timeline_repo, clustering_service=mock_clustering_service, ai_service=mock_ai_service
    )


@pytest.fixture
def sample_token_data() -> TokenData:
    return TokenData(sub=1, email="test@example.com")


# --- Timeline Tests ---
@pytest.mark.asyncio
async def test_get_user_timelines(timeline_service: TimelineService, mock_timeline_repo: AsyncMock) -> None:
    user_id = 1
    mock_timeline_repo.get_timelines_by_user_id.return_value = [Timeline(id=1, title="Test")]

    result = await timeline_service.get_user_timelines(user_id)

    assert len(result) == 1
    mock_timeline_repo.get_timelines_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_timeline_details_tree_construction(
    timeline_service: TimelineService, mock_timeline_repo: AsyncMock
) -> None:
    """Tests that flat nodes are correctly converted into a nested tree structure."""
    user_id = 1
    timeline_id = 10

    # Setup Flat Nodes: 2 Parents, 1 Child for Parent 1, 1 Orphan
    node_p1 = MagicMock(spec=TimelineNode, id=1, parent_id=None, start_date=datetime(2025, 1, 1))
    node_p2 = MagicMock(spec=TimelineNode, id=2, parent_id=None, start_date=datetime(2025, 1, 5))
    node_c1 = MagicMock(spec=TimelineNode, id=3, parent_id=1, start_date=datetime(2025, 1, 2))
    node_orphan = MagicMock(spec=TimelineNode, id=4, parent_id=99, start_date=datetime(2025, 1, 3))

    mock_timeline = MagicMock(spec=Timeline)
    mock_timeline.nodes = [node_p2, node_p1, node_c1, node_orphan]  # Unsorted
    mock_timeline_repo.get_timeline_with_nodes.return_value = mock_timeline

    result = await timeline_service.get_timeline_details(timeline_id, user_id)

    # Assertions
    # 1. Timeline nodes list should only contain top-level nodes (parents)
    assert len(result.nodes) == 2
    assert result.nodes[0].id == 1  # Sorted by date
    assert result.nodes[1].id == 2

    # 2. Child should be attached to parent 1
    assert len(result.nodes[0].children) == 1
    assert result.nodes[0].children[0].id == 3


@pytest.mark.asyncio
async def test_create_timeline(
    timeline_service: TimelineService, sample_token_data: TokenData, mock_timeline_repo: AsyncMock
) -> None:
    timeline_in = TimelineCreate(title="New Timeline", slug="new-timeline")

    await timeline_service.create_timeline(timeline_in, sample_token_data)

    # Verify the model passed to repo has the correct user_id from token
    args, _ = mock_timeline_repo.create_timeline.call_args
    created_model = args[0]
    assert created_model.user_id == sample_token_data.sub
    assert created_model.title == "New Timeline"


# --- Timeline Node Tests ---
@pytest.mark.asyncio
async def test_create_timeline_node_success(timeline_service: TimelineService, mock_timeline_repo: AsyncMock) -> None:
    user_id = 1
    node_in = TimelineNodeCreate(
        timeline_id=10,
        title="Node",
        type="work",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2),
        is_current=False,
    )

    mock_timeline_repo.get_timeline_by_id.return_value = MagicMock(id=10)

    await timeline_service.create_timeline_node(node_in, user_id)

    mock_timeline_repo.create_timeline_node.assert_called_once()


@pytest.mark.asyncio
async def test_create_timeline_node_timeline_not_found(
    timeline_service: TimelineService, mock_timeline_repo: AsyncMock
) -> None:
    mock_timeline_repo.get_timeline_by_id.return_value = None
    node_in = TimelineNodeCreate(timeline_id=99, title="Fail", type="work", is_current=True, start_date=datetime.now())

    with pytest.raises(TimelineNotFoundError):
        await timeline_service.create_timeline_node(node_in, user_id=1)


# --- Validation Helper Tests ---
def test_validate_dates_invalid_current(timeline_service: TimelineService) -> None:
    """Current nodes must not have an end_date."""
    node = TimelineNodeCreate(
        timeline_id=1, title="T", type="work", is_current=True, start_date=datetime.now(), end_date=datetime.now()
    )
    with pytest.raises(InvalidTimelineNodeError) as exc:
        timeline_service._validate_dates(node)
    assert "Current nodes must not have an end_date" in exc.value.details["reason"]


@pytest.mark.asyncio
async def test_validate_dates_backwards(timeline_service: TimelineService) -> None:
    """Start date cannot be after end date."""
    node = TimelineNodeBase(
        title="T", type="work", is_current=False, start_date=datetime(2025, 1, 10), end_date=datetime(2025, 1, 1)
    )
    with pytest.raises(InvalidTimelineNodeError):
        await timeline_service._validate_dates(node)


@pytest.mark.asyncio
async def test_validate_hierarchy_max_depth(timeline_service: TimelineService, mock_timeline_repo: AsyncMock) -> None:
    """Should fail if trying to nest a child under a node that is already a child."""
    timeline_id = 10
    parent_id = 2

    # Parent node itself has a parent_id (it's a child)
    parent_node = MagicMock(id=2, timeline_id=timeline_id, parent_id=1)
    mock_timeline_repo.get_timeline_node_lite.return_value = parent_node

    child_node = TimelineNodeCreate(
        timeline_id=timeline_id,
        type="work",
        title="Child",
        parent_id=parent_id,
        is_current=True,
        start_date=datetime.now(),
    )

    with pytest.raises(InvalidTimelineNodeError) as exc:
        await timeline_service._validate_parent_hierarchy(parent_id, child_node, timeline_id)
    assert "Max depth is 2" in exc.value.details["reason"]


@pytest.mark.asyncio
async def test_validate_hierarchy_date_mismatch(
    timeline_service: TimelineService, mock_timeline_repo: AsyncMock
) -> None:
    """Child cannot start before parent."""
    timeline_id = 10
    parent_id = 2

    parent_node = MagicMock(
        id=2,
        timeline_id=timeline_id,
        parent_id=None,
        is_current=False,
        start_date=datetime(2025, 2, 1),
        end_date=datetime(2025, 3, 1),
    )
    mock_timeline_repo.get_timeline_node_lite.return_value = parent_node

    # Child starts in January, but parent starts in February
    child_node = TimelineNodeCreate(
        timeline_id=timeline_id,
        title="Child",
        type="work",
        parent_id=parent_id,
        is_current=False,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 2, 15),
    )

    with pytest.raises(InvalidTimelineNodeError) as exc:
        await timeline_service._validate_parent_hierarchy(parent_id, child_node, timeline_id)
    assert "Child cannot start before parent" in exc.value.details["reason"]


@pytest.mark.asyncio
async def test_delete_timeline_node_success(timeline_service: TimelineService, mock_timeline_repo: AsyncMock) -> None:
    node_id = 5
    user_id = 1

    # Mocks
    mock_node = MagicMock(timeline_id=10)
    mock_timeline_repo.get_timeline_node_lite.return_value = mock_node
    mock_timeline_repo.get_timeline_by_id.return_value = MagicMock(id=10)

    await timeline_service.delete_timeline_node(node_id, user_id)

    mock_timeline_repo.delete_timeline_node.assert_called_once_with(node_id)


@pytest.mark.asyncio
async def test_generate_nodes_for_commits_hierarchy_and_expansion(
    timeline_service: TimelineService,
    mock_clustering_service: MagicMock,
    mock_ai_service: AsyncMock,
    mock_timeline_repo: AsyncMock,
) -> None:
    # --- Setup ---
    user_id, timeline_id, repo_id = 1, 10, 100
    UTC = timezone.utc

    # Parent: Feb 1 -> Mar 10 | Child: Mar 15 -> Mar 20 (Triggers End Date Expansion)
    cluster_p = MagicMock(
        spec=Cluster,
        is_shallow=False,
        id="c1",
        start_date=datetime(2025, 2, 1, tzinfo=UTC),
        end_date=datetime(2025, 3, 10, tzinfo=UTC),
    )
    cluster_c = MagicMock(
        spec=Cluster,
        is_shallow=False,
        id="c2",
        start_date=datetime(2025, 3, 15, tzinfo=UTC),
        end_date=datetime(2025, 3, 20, tzinfo=UTC),
    )
    mock_clustering_service.cluster_commits.return_value = [cluster_p, cluster_c]

    # Mock AI Responses
    ai_p = AnalysisResult(
        action=AnalysisAction.CREATE_NODE,
        reasoning="Major feature identified",
        node_content=TimelineNodeBase(
            title="Parent",
            type="project",
            is_current=False,
            start_date=cluster_p.start_date,
            end_date=cluster_p.end_date,
        ),
    )
    ai_c = AnalysisResult(
        action=AnalysisAction.MERGE_TO_PARENT,
        reasoning="Minor follow-up work",
        node_content=TimelineNodeBase(
            title="Child",
            type="project",
            is_current=False,
            start_date=cluster_c.start_date,
            end_date=cluster_c.end_date,
        ),
    )
    mock_ai_service.analyze_cluster.side_effect = [ai_p, ai_c]

    # --- Parent Mock Fix ---
    parent_node_db = MagicMock()
    parent_node_db.id = 55
    parent_node_db.timeline_id = timeline_id
    parent_node_db.start_date = cluster_p.start_date
    parent_node_db.end_date = cluster_p.end_date
    parent_node_db.is_current = False
    parent_node_db.parent_id = None

    # Mock Repository
    mock_timeline_repo.get_timeline_by_id.return_value = MagicMock(id=timeline_id)
    mock_timeline_repo.get_timeline_node_by_id.return_value = parent_node_db
    mock_timeline_repo.get_timeline_node_lite.return_value = parent_node_db
    mock_timeline_repo.create_timeline_node.side_effect = [parent_node_db, MagicMock(id=56)]

    # --- Execute ---
    await timeline_service.generate_nodes_for_commits([], timeline_id, repo_id, user_id)

    # --- Assertions ---
    assert mock_timeline_repo.create_timeline_node.call_count == 2

    mock_timeline_repo.update_timeline_node.assert_called_once()
    assert parent_node_db.end_date.date() == cluster_c.end_date.date()
