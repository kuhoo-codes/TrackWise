from src.schemas.integrations.ai.timeline_analysis import AnalysisAction, AnalysisResult
from src.schemas.integrations.analysis.cluster import Cluster
from src.schemas.timelines import DateGranularity, NodeType
from src.services.integrations.ai.base_provider import AIProvider


class TimelineAnalysisService:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def analyze_cluster(self, cluster: Cluster, repo_id: int) -> AnalysisResult:
        """Orchestrates the context building and provider execution."""
        context = self._build_context(cluster)
        result = await self.provider.analyze_payload(context)

        if result.action == AnalysisAction.CREATE_NODE and result.node_content:
            result.node_content.github_repo_id = repo_id
            result.node_content.start_date = cluster.start_date
            result.node_content.end_date = cluster.end_date
            result.node_content.type = NodeType.PROJECT
            result.node_content.date_granularity = DateGranularity.EXACT

        return result

    def _build_context(self, cluster: Cluster) -> str:
        """Refined prompt context for high-quality achievement extraction."""
        msgs = [m.message for m in cluster.items[:25]]  # Cap for tokens

        files = set()
        for item in cluster.items:
            for f in item.files or []:
                files.add(f.get("filename", ""))

        return f"""
        TASK: Analyze the following developer activity and decide if it warrants a timeline entry.
        DATA:
        - Work Topic: {cluster.topic}
        - Intensity Score: {cluster.impact_score} (Higher means more lines/complexity)
        - Tech Stack Detected: {", ".join(cluster.primary_file_types)}
        - Key Files: {list(files)[:15]}
        - Commit Log:
        {chr(10).join(f"- {m}" for m in msgs)}

        GUIDELINES FOR DECISION:
        1. Action:
           - CREATE_NODE: Use this for logic-heavy features, refactors, or new modules.
           - MERGE_TO_PARENT: Use for minor bug fixes or small incremental improvements.
           - IGNORE: Use for documentation typos, configuration boilerplate, or minor noise.

        2. Content (If CREATE_NODE):
           - Title: Make it Professional.
           - Short Summary: 1-sentence punchy value proposition.
           - Description: Use Markdown. Focus on 'Solved X by doing Y resulting in Z'.
        """
