import os
from collections import Counter
from datetime import timedelta

from src.schemas.integrations.analysis.cluster import Cluster
from src.schemas.integrations.analysis.significance import SignificanceLevel
from src.schemas.integrations.github import CommitInDB


class ActivityClusteringService:
    def __init__(self, window_days: int = 7, shallow_threshold: float = 5.0) -> None:
        self.window_days = timedelta(days=window_days)
        self.shallow_threshold = shallow_threshold

    def cluster_commits(self, commits: list[CommitInDB]) -> list[Cluster]:
        """
        Clusters commits using a sliding time window and directory heuristics.
        Expects commits sorted by date (asc).
        """
        if not commits:
            return []

        sorted_commits = sorted(commits, key=lambda x: x.authored_at)

        clusters = []
        current_batch = [sorted_commits[0]]

        for i in range(1, len(sorted_commits)):
            prev_commit = sorted_commits[i - 1]
            curr_commit = sorted_commits[i]

            # Time-Based Clustering (7-day sliding window)
            if curr_commit.authored_at - prev_commit.authored_at <= self.window_days:
                current_batch.append(curr_commit)
            else:
                clusters.append(self._create_cluster_object(current_batch))
                current_batch = [curr_commit]

        if current_batch:
            clusters.append(self._create_cluster_object(current_batch))

        return clusters

    def _get_topic_from_paths(self, file_paths: list[str]) -> str:
        """
        Extracts the most common meaningful directory from paths.
        Example: src/auth/login.py -> 'auth'
        """
        directories = []
        for path in file_paths:
            parts = path.split(os.sep)
            # Ignore root files (len <= 1) and common top-levels like 'src' or 'app'
            if len(parts) > 1:
                topic = parts[1] if parts[0] in ["src", "app", "lib", "packages"] else parts[0]
                directories.append(topic)
        if not directories:
            return "general"

        counts = Counter(directories)
        most_common, frequency = counts.most_common(1)[0]

        # Directory-Based Sub-Clustering Bonus: Only tag if it represents > 80% of changes
        if (frequency / len(directories)) >= 0.8:
            return most_common
        return "general"

    def _create_cluster_object(self, batch: list[CommitInDB]) -> Cluster:
        """Helper to aggregate data from a batch of commits into a Cluster."""
        all_files = []
        all_exts = []
        all_types = []
        total_impact = 0.0

        for commit in batch:
            total_impact += commit.significance_score if commit.significance_score is not None else 0
            all_types.append(commit.significance_classification)

            for f in commit.files:
                all_files.append(f["filename"])
                _, ext = os.path.splitext(f["filename"])
                if ext:
                    all_exts.append(ext)

        # Heuristics for metadata
        topic = self._get_topic_from_paths(all_files)
        most_frequent_type = Counter(all_types).most_common(1)[0][0]
        unique_exts = list(set(all_exts))

        return Cluster(
            id=f"cluster_{batch[0].authored_at.strftime('%Y%m%d')}_{topic}",
            topic=topic,
            start_date=batch[0].authored_at,
            end_date=batch[-1].authored_at,
            items=batch,
            primary_file_types=unique_exts[:3],
            suggested_type=SignificanceLevel(most_frequent_type),
            impact_score=round(total_impact, 2),
            is_shallow=total_impact < self.shallow_threshold,
        )
