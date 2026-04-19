from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.repositories.integrations.external_profile_repository import ExternalProfileRepository
from src.repositories.integrations.github_repository import GithubRepository
from src.repositories.timeline_repository import TimelineRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.integrations.ai.providers.gemini_provider import GeminiProvider
from src.services.integrations.ai.providers.ollama_provider import OllamaProvider
from src.services.integrations.ai.timeline_analysis_service import TimelineAnalysisService
from src.services.integrations.analysis.activity_clustering_service import ActivityClusteringService
from src.services.integrations.analysis.significance_analyzer_service import SignificanceAnalyzerService
from src.services.integrations.github_service import GithubService
from src.services.timeline_service import TimelineService


class ServiceFactory:
    @staticmethod
    def create_auth_service(db: AsyncSession) -> AuthService:
        return AuthService(UserRepository(db))

    @staticmethod
    def create_timeline_service(db: AsyncSession) -> TimelineService:
        # 1. Initialize Repository
        repo = TimelineRepository(db)

        # 2. Initialize Clustering Logic (Phase 2)
        clustering = ActivityClusteringService()

        # 3. Initialize AI Provider (Phase 3)
        # Switch this to GeminiProvider(settings.GEMINI_API_KEY) for production
        if settings.ENVIRONMENT == "development":
            ai_provider = OllamaProvider()
        else:
            ai_provider = GeminiProvider(api_key=settings.GEMINI_API_KEY)

        ai_service = TimelineAnalysisService(provider=ai_provider)

        # 4. Return the fully composed Service
        return TimelineService(timeline_repo=repo, clustering_service=clustering, ai_service=ai_service)

    @staticmethod
    def create_github_service(db: AsyncSession) -> GithubService:
        timeline_service = ServiceFactory.create_timeline_service(db)
        return GithubService(
            repo=GithubRepository(db),
            external_profile_repo=ExternalProfileRepository(db),
            analyzer_service=SignificanceAnalyzerService(),
            timeline_service=timeline_service,
        )
