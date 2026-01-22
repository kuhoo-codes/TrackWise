import fnmatch
import math
import os

from src.schemas.integrations.significance import FileChange, SignificanceLevel, SignificanceResult
from src.services.integrations.constants import (
    HIGH_VALUE_EXTS,
    IGNORED_PATTERNS,
    LOW_VALUE_EXTS,
    MAX_LINES_PER_FILE_CAP,
    MEDIUM_VALUE_FILES,
    WEIGHTS,
)


class SignificanceAnalyzerService:
    def _check_keywords(self, message: str) -> float:
        """Returns a multiplier based on the commit message content."""
        msg = message.lower()
        if any(word in msg for word in ["feat", "add", "new", "implement"]):
            return 1.2  # Boost for features
        if any(word in msg for word in ["refactor", "lint", "format", "style", "pretty"]):
            return 0.5  # Heavy penalty for mechanical changes
        if any(word in msg for word in ["fix", "bug", "patch"]):
            return 1.1  # Slight boost for fixes
        return 1.0

    def _get_file_weight(self, filename: str) -> float:
        """Determines the weight of a file based on its name and extension."""
        basename = os.path.basename(filename)
        _, ext = os.path.splitext(filename)

        for pattern in IGNORED_PATTERNS:
            if fnmatch.fnmatch(filename, pattern):
                return 0.0

        if basename in MEDIUM_VALUE_FILES or ".github/workflows" in filename:
            return WEIGHTS["MEDIUM"]

        if ext in HIGH_VALUE_EXTS:
            return WEIGHTS["HIGH"]

        if ext in LOW_VALUE_EXTS:
            return WEIGHTS["LOW"]

        return 0.2

    def analyze_commit(self, message: str, files: list[FileChange]) -> SignificanceResult:
        """
        Calculates a significance score based on the heuristic:
        score = sum((capped_changes) * file_weight)
        """
        if not files:
            return SignificanceResult(score=0, classification=SignificanceLevel.NOISE, is_significant=False)

        file_count = len(files)
        weighted_scores = []

        for file in files:
            weight = self._get_file_weight(file.filename)
            changes = file.additions + file.deletions
            effective_changes = min(changes, MAX_LINES_PER_FILE_CAP)
            weighted_scores.append(effective_changes * weight)

        total_raw_score = sum(weighted_scores)

        # A "Focus Factor" penalizes commits that are spread too thin across many files.
        focus_factor = 1.0 / math.log2(file_count + 1)

        keyword_multiplier = self._check_keywords(message)

        avg_change = total_raw_score / file_count
        final_score = total_raw_score * focus_factor * keyword_multiplier

        is_mechanical = avg_change < 3.0 and file_count > 5
        is_concentrated = avg_change > 15.0 and file_count <= 5

        if is_concentrated or (final_score >= 20 and not is_mechanical):
            classification = SignificanceLevel.FEATURE

        elif is_mechanical or total_raw_score > 50:
            classification = SignificanceLevel.REFACTOR

        elif final_score > 0:
            classification = SignificanceLevel.CHORE
        else:
            classification = SignificanceLevel.NOISE

        return SignificanceResult(
            score=round(final_score, 2),
            classification=classification,
            is_significant=classification in [SignificanceLevel.FEATURE, SignificanceLevel.REFACTOR],
        )
