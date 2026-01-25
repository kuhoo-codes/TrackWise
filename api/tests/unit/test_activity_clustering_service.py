from datetime import datetime, timedelta, timezone

import pytest

from src.schemas.integrations.analysis.significance import SignificanceLevel
from src.schemas.integrations.github import CommitInDB
from src.services.integrations.analysis.activity_clustering_service import ActivityClusteringService


@pytest.fixture
def clustering_service() -> ActivityClusteringService:
    """Fixture for the ActivityClusteringService."""
    return ActivityClusteringService(window_days=7, shallow_threshold=5.0)


def create_mock_commit(
    days_offset: int, score: float, classification: SignificanceLevel, files: list[str]
) -> CommitInDB:
    """Helper to generate a CommitInDB object for testing."""
    return CommitInDB(
        sha=f"sha_{days_offset}",
        external_profile_id=1,
        author_id=1,
        repository_id=1,
        message="Test commit",
        authored_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=days_offset),
        html_url="http://github.com",
        additions=10,
        deletions=2,
        total=12,
        files=[{"filename": f} for f in files],
        significance_score=score,
        significance_classification=classification,
    )


# --- Tests for Sliding Window Logic ---


def test_cluster_commits_sliding_window(clustering_service: ActivityClusteringService) -> None:
    """Verify that commits within 7 days are grouped, and gaps start new clusters."""
    commits = [
        create_mock_commit(0, 10.0, SignificanceLevel.FEATURE, ["src/auth/a.py"]),
        create_mock_commit(3, 5.0, SignificanceLevel.FEATURE, ["src/auth/b.py"]),
        create_mock_commit(12, 8.0, SignificanceLevel.FEATURE, ["src/api/c.py"]),  # 9 days gap from prev
    ]

    clusters = clustering_service.cluster_commits(commits)

    assert len(clusters) == 2
    assert len(clusters[0].items) == 2  # Days 0 and 3
    assert len(clusters[1].items) == 1  # Day 12
    assert clusters[0].topic == "auth"
    assert clusters[1].topic == "api"


# --- Tests for Topic Extraction (_get_topic_from_paths) ---


@pytest.mark.parametrize(
    "file_paths, expected_topic",
    [
        (
            [
                "src/auth/login.py",
                "src/auth/session.py",
                "src/auth/signup.py",
                "src/auth/logout.py",
                "src/ui/button.tsx",
            ],
            "auth",
        ),
        (["src/auth/login.py", "src/auth/signup.py", "src/auth/logout.py", "src/ui/button.tsx"], "general"),
        (["src/auth/login.py", "src/auth/session.py", "src/auth/token.py"], "auth"),
        (["app/models/user.py", "app/models/post.py"], "models"),
        (["root_file.py", "README.md"], "general"),
        (["src/api/v1/user.py", "src/ui/header.tsx"], "general"),
    ],
)
def test_get_topic_from_paths(
    clustering_service: ActivityClusteringService, file_paths: list[str], expected_topic: str
) -> None:
    """Test the 80% threshold and directory depth logic."""
    assert clustering_service._get_topic_from_paths(file_paths) == expected_topic


# --- Tests for Cluster Aggregation & Metadata ---


def test_create_cluster_object_metadata(clustering_service: ActivityClusteringService) -> None:
    """Verify that cluster metadata (impact, extensions, dates) is aggregated correctly."""
    commits = [
        create_mock_commit(0, 2.0, SignificanceLevel.CHORE, ["src/auth/a.py"]),
        create_mock_commit(1, 2.0, SignificanceLevel.CHORE, ["src/auth/b.ts"]),
    ]

    clusters = clustering_service.cluster_commits(commits)
    cluster = clusters[0]

    assert cluster.impact_score == 4.0
    assert cluster.is_shallow is True  # 4.0 < 5.0 threshold
    assert set(cluster.primary_file_types) == {".py", ".ts"}
    assert cluster.suggested_type == SignificanceLevel.CHORE
    assert cluster.start_date == commits[0].authored_at
    assert cluster.end_date == commits[1].authored_at


def test_shallow_threshold_logic(clustering_service: ActivityClusteringService) -> None:
    """Verify that impact score determines the is_shallow flag."""
    # Score 6.0 > 5.0 threshold
    commits_rich = [create_mock_commit(0, 6.0, SignificanceLevel.FEATURE, ["src/api/a.py"])]
    # Score 2.0 < 5.0 threshold
    commits_shallow = [create_mock_commit(0, 2.0, SignificanceLevel.CHORE, ["src/api/a.py"])]

    cluster_rich = clustering_service.cluster_commits(commits_rich)[0]
    cluster_shallow = clustering_service.cluster_commits(commits_shallow)[0]

    assert cluster_rich.is_shallow is False
    assert cluster_shallow.is_shallow is True


# --- Tests for Edge Cases ---


def test_cluster_empty_list(clustering_service: ActivityClusteringService) -> None:
    """Ensure empty input returns empty output."""
    assert clustering_service.cluster_commits([]) == []


def test_cluster_id_generation(clustering_service: ActivityClusteringService) -> None:
    """Verify the ID format follows 'cluster_YYYYMMDD_topic'."""
    commit = create_mock_commit(0, 10.0, SignificanceLevel.FEATURE, ["src/auth/a.py"])
    cluster = clustering_service.cluster_commits([commit])[0]

    # Date 2026-01-01 -> 20260101
    assert cluster.id == "cluster_20260101_auth"
