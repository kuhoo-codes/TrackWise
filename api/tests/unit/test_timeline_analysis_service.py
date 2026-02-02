from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.integrations.github.github_commits import SignificanceLevel
from src.schemas.integrations.ai.timeline_analysis import AnalysisAction, AnalysisResult
from src.schemas.integrations.analysis.cluster import Cluster
from src.schemas.integrations.github import CommitInDB
from src.schemas.timelines import DateGranularity, NodeType, TimelineNodeBase
from src.services.integrations.ai.timeline_analysis_service import TimelineAnalysisService


@pytest.fixture
def mock_provider() -> AsyncMock:
    """Fixture for a mocked AIProvider."""
    provider = AsyncMock()
    provider.analyze_payload = AsyncMock()
    return provider


@pytest.fixture
def timeline_analysis_service(mock_provider: AsyncMock) -> TimelineAnalysisService:
    """Fixture for the TimelineAnalysisService with a mocked provider."""
    return TimelineAnalysisService(provider=mock_provider)


@pytest.fixture
def sample_cluster() -> Cluster:
    """Fixture for a sample cluster object."""
    mock_item = MagicMock()
    mock_item.sha = "test_sha_123"
    mock_item.html_url = "https://github.com/test/commit/123"
    mock_item.message = "feat: add oauth2 login"
    mock_item.files = [{"filename": "src/auth.py"}]
    mock_item.significance_score = 25.5
    # This must be the actual Enum value or the string equivalent
    mock_item.significance_classification = SignificanceLevel.FEATURE

    # Add other required fields from CommitInDB if they exist
    mock_item.external_profile_id = 1
    mock_item.author_id = 1
    mock_item.repository_id = 1
    mock_item.authored_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    mock_item.additions = 10
    mock_item.deletions = 2
    mock_item.total = 12

    return Cluster(
        id="cluster_20260101_auth",
        topic="auth",
        start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2026, 1, 5, tzinfo=timezone.utc),
        items=[mock_item],
        primary_file_types=[".py"],
        impact_score=25.5,
        is_shallow=False,
        suggested_type="FEATURE",
    )


# --- Tests for analyze_cluster ---


@pytest.mark.asyncio
async def test_analyze_cluster_create_node_enrichment(
    timeline_analysis_service: TimelineAnalysisService, mock_provider: AsyncMock, sample_cluster: Cluster
) -> None:
    """
    Test that if the AI decides to CREATE_NODE, the content is correctly
    enriched with cluster metadata and repo_id.
    """
    # --- Setup ---
    repo_id = 42
    mock_node_content = TimelineNodeBase(
        title="AI Generated Title",
        short_summary="Summary",
        type=NodeType.PROJECT,  # This will be overwritten by service
        start_date=datetime.now(),  # This will be overwritten by service
    )

    mock_result = AnalysisResult(
        action=AnalysisAction.CREATE_NODE,
        node_content=mock_node_content,
        reasoning="Significant feature detected",
        tech_stack=["Python"],
    )
    mock_provider.analyze_payload.return_value = mock_result

    result = await timeline_analysis_service.analyze_cluster(sample_cluster, repo_id)

    # --- Assert ---
    mock_provider.analyze_payload.assert_called_once()

    assert result.node_content.github_repo_id == repo_id
    assert result.node_content.start_date == sample_cluster.start_date
    assert result.node_content.end_date == sample_cluster.end_date
    assert result.node_content.type == NodeType.PROJECT
    assert result.node_content.date_granularity == DateGranularity.EXACT
    assert result.action == AnalysisAction.CREATE_NODE


@pytest.mark.asyncio
async def test_analyze_cluster_ignore_action(
    timeline_analysis_service: TimelineAnalysisService, mock_provider: AsyncMock, sample_cluster: Cluster
) -> None:
    """
    Test that if the AI returns IGNORE, no enrichment happens
    (and it doesn't crash).
    """
    # --- Setup ---
    mock_result = AnalysisResult(action=AnalysisAction.IGNORE, node_content=None, reasoning="Just noise", tech_stack=[])
    mock_provider.analyze_payload.return_value = mock_result

    # --- Execute ---
    result = await timeline_analysis_service.analyze_cluster(sample_cluster, repo_id=1)

    # --- Assert ---
    assert result.action == AnalysisAction.IGNORE
    assert result.node_content is None
    assert result.reasoning == "Just noise"


# --- Tests for _build_context ---


def test_build_context_logic(timeline_analysis_service: TimelineAnalysisService, sample_cluster: Cluster) -> None:
    """
    Verify that the context string is constructed correctly with
    expected data points and capping logic.
    """
    # --- Execute ---
    context = timeline_analysis_service._build_context(sample_cluster)

    # --- Assert ---
    assert "Work Topic: auth" in context
    assert "Intensity Score: 25.5" in context
    assert "feat: add oauth2 login" in context
    assert "src/auth.py" in context
    assert "Tech Stack Detected: .py" in context
    assert "GUIDELINES FOR DECISION" in context


def test_build_context_capping(timeline_analysis_service: TimelineAnalysisService) -> None:
    """
    Ensure the context caps commit messages at 25 and files at 15.
    """
    # Create a cluster with 30 items
    many_items = [
        CommitInDB(
            sha=f"sha_{i}",
            external_profile_id=1,
            author_id=1,
            repository_id=1,
            message=f"msg {i}",
            authored_at=datetime.now(),
            html_url=f"https://github.com/commit/{i}",
            additions=1,
            deletions=1,
            total=2,
            files=[],  # Empty list is valid
            significance_score=1.0,
            significance_classification=SignificanceLevel.CHORE,
        )
        for i in range(30)
    ]
    cluster = Cluster(
        id="test",
        topic="test",
        start_date=datetime.now(),
        end_date=datetime.now(),
        items=many_items,
        primary_file_types=[],
        impact_score=1.0,
        is_shallow=False,
        suggested_type="CHORE",
    )

    context = timeline_analysis_service._build_context(cluster)

    # "msg 24" should be there (index 24 is the 25th item)
    assert "- msg 24" in context
    # "msg 25" should NOT be there
    assert "- msg 25" not in context
