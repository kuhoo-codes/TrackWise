import pytest

from src.schemas.integrations.significance import FileChange, SignificanceLevel
from src.services.integrations.significance_analyzer_service import SignificanceAnalyzerService


@pytest.fixture
def significance_service() -> SignificanceAnalyzerService:
    """Fixture for the SignificanceAnalyzerService."""
    return SignificanceAnalyzerService()


# --- Tests for _get_file_weight ---


@pytest.mark.parametrize(
    "filename, expected_weight",
    [
        ("main.py", 1.0),
        ("index.ts", 1.0),
        ("Dockerfile", 0.5),
        (".github/workflows/main.yml", 0.5),
        ("README.md", 0.1),
        ("package-lock.json", 0.0),
        ("dist/bundle.js", 0.0),
        ("config.json", 0.1),
        ("random_file.xyz", 0.2),
    ],
)
def test_get_file_weight(
    significance_service: SignificanceAnalyzerService, filename: str, expected_weight: float
) -> None:
    """Test that file weights are correctly assigned based on patterns and extensions."""
    assert significance_service._get_file_weight(filename) == expected_weight


# --- Tests for _check_keywords ---


@pytest.mark.parametrize(
    "message, expected_multiplier",
    [
        ("feat: add new timeline feature", 1.2),
        ("fix: resolve database deadlock", 1.1),
        ("refactor: clean up loop logic", 0.5),
        ("lint: fix formatting with prettier", 0.5),
        ("initial commit", 1.0),
    ],
)
def test_check_keywords(
    significance_service: SignificanceAnalyzerService, message: str, expected_multiplier: float
) -> None:
    """Test that commit message keywords return the correct score multipliers."""
    assert significance_service._check_keywords(message) == expected_multiplier


# --- Tests for analyze_commit ---


def test_analyze_commit_no_files(significance_service: SignificanceAnalyzerService) -> None:
    """Empty file list should return NOISE."""
    result = significance_service.analyze_commit("empty", [])
    assert result.classification == SignificanceLevel.NOISE
    assert result.score == 0
    assert result.is_significant is False


def test_analyze_commit_feature_high_density(significance_service: SignificanceAnalyzerService) -> None:
    """Small file count with high core logic changes should be a FEATURE."""
    files = [
        FileChange(filename="src/app.py", additions=100, deletions=20),
        FileChange(filename="src/utils.py", additions=50, deletions=10),
    ]
    # (120 * 1.0) + (60 * 1.0) = 180 raw.
    # focus_factor = 1 / log2(3) approx 0.63. Score approx 113.
    result = significance_service.analyze_commit("feat: core logic", files)

    assert result.classification == SignificanceLevel.FEATURE
    assert result.is_significant is True
    assert result.score > 50


def test_analyze_commit_refactor_low_density(significance_service: SignificanceAnalyzerService) -> None:
    """High file count with minimal changes per file should be classified as REFACTOR."""
    # 20 files, 2 lines each = 40 raw. avg_change = 2.0 (Mechanical)
    files = [FileChange(filename=f"ui/file_{i}.tsx", additions=2, deletions=0) for i in range(20)]

    result = significance_service.analyze_commit("style: camelCase rename", files)

    assert result.classification == SignificanceLevel.REFACTOR
    assert result.is_significant is True


def test_analyze_commit_capping_logic(significance_service: SignificanceAnalyzerService) -> None:
    """Ensure that massive file changes are capped to prevent score inflation."""
    # 10,000 additions in one .py file.
    files = [FileChange(filename="large_file.py", additions=10000, deletions=0)]

    result = significance_service.analyze_commit("add massive file", files)

    # Raw score capped at 500 * 1.0 * 1.2 = 600. focus_factor = 1.0. keyword_multiplier = 1.2
    assert result.score == 600.0
    assert result.classification == SignificanceLevel.FEATURE


def test_analyze_commit_chore_documentation(significance_service: SignificanceAnalyzerService) -> None:
    """Pure documentation updates should result in a CHORE classification."""
    files = [FileChange(filename="README.md", additions=50, deletions=0)]

    result = significance_service.analyze_commit("docs: update instructions", files)

    # 50 * 0.1 = 5.0 raw.
    assert result.classification == SignificanceLevel.CHORE
    assert result.is_significant is False
