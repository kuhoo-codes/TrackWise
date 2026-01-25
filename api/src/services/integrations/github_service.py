import asyncio
import secrets
from datetime import datetime, timezone
from typing import Annotated

import httpx
from loguru import logger
from pydantic import TypeAdapter

from src.core.config import Errors, GithubRoutes, settings
from src.exceptions.external import GitHubIntegrationError
from src.models.integrations import ExternalProfile, PlatformEnum, SyncStatusEnum, SyncStepEnum
from src.models.integrations.github import GithubRepository as GithubRepoModel
from src.repositories.integrations.external_profile_repository import ExternalProfileRepository
from src.repositories.integrations.github_repository import GithubRepository
from src.schemas.integrations.analysis.significance import FileChange
from src.schemas.integrations.github import Commit, GithubToken, Issue, RepoCommit, Repository, TokenResponse, User
from src.services.integrations.analysis.significance_analyzer_service import SignificanceAnalyzerService


class GithubService:
    def __init__(
        self,
        repo: GithubRepository,
        external_profile_repo: ExternalProfileRepository,
        analyzer_service: SignificanceAnalyzerService,
    ) -> None:
        self.repo = repo
        self.external_profile_repo = external_profile_repo
        self.analyzer_service = analyzer_service
        self.GITHUB_API_URL = settings.GITHUB_BASE_API_URL
        self.GITHUB_ROUTES = GithubRoutes
        self.PER_PAGE = settings.GITHUB_PER_PAGE
        self.semaphore = asyncio.Semaphore(10)

    async def get_auth_url(self, user_id: Annotated[str, "Associated user ID"]) -> str:
        """Generate GitHub OAuth authorization URL."""
        state = secrets.token_urlsafe(16)
        await self.repo.save_state(state, user_id)

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{httpx.QueryParams(params)}"

    async def handle_callback(self, code: str, state: Annotated[str, "GitHub OAuth state parameter"]) -> TokenResponse:
        """Handle GitHub OAuth callback and exchange code for token."""
        state_record = await self.repo.validate_state(state)
        user_id = state_record.user_id
        github_token = await self.exchange_github_code(
            code=code, client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_CLIENT_SECRET
        )
        await self.repo.save_token(user_id, github_token)
        external_profile = await self.external_profile_repo.get_external_profile_by_user_id(
            user_id, PlatformEnum.GITHUB
        )
        if external_profile:
            logger.info("Updating existing external profile for user_id: {}", user_id)
            await self.update_external_profile_token(external_profile, github_token)
        else:
            logger.info("Creating new external profile for user_id: {}", user_id)
            github_user = await self.get_auth_user(github_token.access_token)
            await self.create_external_profile(github_user, user_id, github_token)
        return TokenResponse(access_token=github_token.access_token, token_type=github_token.token_type)

    async def exchange_github_code(self, code: str, client_id: str, client_secret: str) -> GithubToken:
        """Handle GitHub OAuth code exchange"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                json={"client_id": client_id, "client_secret": client_secret, "code": code},
                headers={"Accept": "application/json"},
            )
        data = response.json()

        if "error" in data:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": data.get("error_description")}
            )

        return GithubToken(**data)

    async def create_external_profile(
        self, github_user: User, user_id: int, github_token: GithubToken
    ) -> ExternalProfile:
        """Create a new ExternalProfile for the user."""
        external_profile = ExternalProfile(
            external_id=github_user.id,
            user_id=user_id,
            platform=PlatformEnum.GITHUB,
            external_username=github_user.login,
            access_token=github_token.access_token,
            refresh_token=github_token.refresh_token,
            access_token_expires_at=github_token.access_token_expires_at,
            refresh_token_expires_at=github_token.refresh_token_expires_at,
            last_synced_at=None,
        )

        return await self.external_profile_repo.create_external_profile(external_profile)

    async def update_external_profile_token(
        self, external_profile: ExternalProfile, github_token: GithubToken
    ) -> ExternalProfile:
        """Update tokens and expiration times for an existing ExternalProfile."""
        external_profile.access_token = github_token.access_token
        external_profile.refresh_token = github_token.refresh_token
        external_profile.access_token_expires_at = github_token.access_token_expires_at
        external_profile.refresh_token_expires_at = github_token.refresh_token_expires_at

        return await self.external_profile_repo.update_external_profile(external_profile)

    async def get_external_profile(self, user_id: int) -> ExternalProfile:
        """Fetch the GitHub ExternalProfile for a given user."""
        return await self.external_profile_repo.get_external_profile_by_user_id(user_id, PlatformEnum.GITHUB)

    async def get_valid_access_token(self, user_id: int) -> tuple[str, ExternalProfile]:
        """Retrieve a valid GitHub access token, refreshing if necessary."""
        external_profile = await self.external_profile_repo.get_external_profile_by_user_id(
            user_id, PlatformEnum.GITHUB
        )
        if not external_profile:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": "GitHub external profile not found"}
            )
        expires_at = external_profile.refresh_token_expires_at
        if expires_at.tzinfo is None:
            logger.warning("Naive datetime detected for refresh_token_expires_at, assuming UTC.")
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": "GitHub token has expired"}
            )
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": external_profile.refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://github.com/login/oauth/access_token?{httpx.QueryParams(params)}",
                headers={"Accept": "application/json"},
            )
        data = response.json()

        if "error" in data:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": data.get("error_description")}
            )

        github_token = GithubToken(**data)
        await self.update_external_profile_token(external_profile, github_token)
        return github_token.access_token, external_profile

    async def get_auth_user(self, access_token: str) -> User:
        """Fetch authenticated user's GitHub profile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GITHUB_API_URL}/{self.GITHUB_ROUTES.USER}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"{settings.TOKEN_TYPE} {access_token}",
                },
            )

            response.raise_for_status()
            adapter = TypeAdapter(User)
            return adapter.validate_python(response.json())

    async def run_full_sync(self, access_token: str, github_profile: ExternalProfile) -> None:
        """This is the main function called by the background task."""
        last_step = github_profile.sync_step
        profile_id = github_profile.id
        try:
            logger.info("Starting full sync for GitHub profile ID: {}", profile_id)
            await self.external_profile_repo.set_sync_status(profile_id, SyncStatusEnum.SYNCING)
            timeout = httpx.Timeout(10.0, connect=5.0, read=30.0, write=10.0)
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"{settings.TOKEN_TYPE} {access_token}",
            }

            async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
                if last_step == SyncStepEnum.NONE:
                    logger.info("Syncing repositories for GitHub profile ID: {}", profile_id)
                    db_repos = await self.sync_repositories(client, github_profile.external_username, profile_id)
                    await self.external_profile_repo.set_sync_step(profile_id, SyncStepEnum.REPOS)
                    last_step = SyncStepEnum.REPOS
                else:
                    logger.info(
                        "Skipping repository sync for GitHub profile ID: {}. Last completed step: {}",
                        profile_id,
                        last_step,
                    )
                    db_repos = await self.repo.get_db_repositories(github_profile.id)

                repos_id_map = {repo.full_name: repo.id for repo in db_repos}

                if last_step == SyncStepEnum.REPOS:
                    logger.info("Syncing issues for GitHub profile ID: {}", profile_id)
                    await self.sync_issues(client, profile_id, repos_id_map)
                    await self.external_profile_repo.set_sync_step(profile_id, SyncStepEnum.ISSUES)
                    last_step = SyncStepEnum.ISSUES
                else:
                    logger.info(
                        "Skipping issues sync for GitHub profile ID: {}. Last completed step: {}", profile_id, last_step
                    )

                if last_step == SyncStepEnum.ISSUES:
                    logger.info("Syncing commits for GitHub profile ID: {}", profile_id)
                    await self.sync_solo_commits(client, github_profile.external_username, profile_id, db_repos)
                    await self.external_profile_repo.set_sync_step(profile_id, SyncStepEnum.COMMITS)
                    last_step = SyncStepEnum.COMMITS
                else:
                    logger.info(
                        "Skipping commits sync for GitHub profile ID: {}. Last completed step: {}",
                        profile_id,
                        last_step,
                    )

                await self.external_profile_repo.set_sync_status(profile_id, SyncStatusEnum.COMPLETED)

                # Reset the step to NONE so the *next* sync runs everything
                await self.external_profile_repo.set_sync_step(profile_id, SyncStepEnum.NONE)
                logger.info("Completed full sync for GitHub profile ID: {}", profile_id)

        except Exception as e:
            await self.external_profile_repo.set_sync_status(profile_id, SyncStatusEnum.FAILED, str(e))
            raise GitHubIntegrationError(Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": str(e)}) from e

        finally:
            profile = await self.get_external_profile(github_profile.user_id)
            if profile.sync_status == SyncStatusEnum.SYNCING:
                await self.external_profile_repo.set_sync_status(profile_id, SyncStatusEnum.IDLE)

    async def sync_repositories(
        self, client: httpx.AsyncClient, username: str, external_profile_id: int
    ) -> list[GithubRepoModel]:
        """Fetches repos from GitHub AND upserts them, returning the DB models."""
        repos_data: list[Repository] = await self.fetch_all_repositories(client, username)
        if not repos_data:
            logger.info("No repositories found for user: {}", username)
            return []

        return await self.repo.bulk_upsert_repositories(repos_data, external_profile_id)

    async def sync_issues(
        self, client: httpx.AsyncClient, external_profile_id: int, repo_id_map: dict[str, int]
    ) -> None:
        """Fetches issues from GitHub AND upserts them into the DB."""
        issues: list[Issue] = await self.fetch_user_issues(client)

        if not issues:
            logger.info("No issues found for external profile ID: {}", external_profile_id)
            return

        await self.repo.bulk_upsert_issues(issues, external_profile_id, repo_id_map)

    async def sync_solo_commits(
        self, client: httpx.AsyncClient, username: str, external_profile_id: int, db_repos: list[GithubRepoModel]
    ) -> None:
        """Fetches and saves commit details for non-forked repos."""

        for repo in db_repos:
            if repo.is_fork:
                logger.info("Skipping forked repository: {}", repo.full_name)
                continue
            sync_start_date = repo.last_commit_sync_at

            lightweight_commits = await self.fetch_author_commits_for_repo(
                client, repo.full_name, username, sync_start_date
            )

            if not lightweight_commits:
                logger.info(
                    "No new commits found for repository '{}' since {}.",
                    repo.full_name,
                    sync_start_date,
                )
                continue

            detailed_commits = await self.fetch_details_for_commits(client, lightweight_commits)

            if detailed_commits:
                await self.repo.bulk_upsert_commit_details(detailed_commits, external_profile_id, repo.id)
                await self.repo.update_repo_sync_time(repo.id)
            else:
                logger.info("Could not fetch detailed commits fetched for repository: {}", repo.full_name)

    async def fetch_user_issues(self, client: httpx.AsyncClient) -> list[Issue]:
        """Fetch all issues assigned to the authenticated user."""
        all_issues = []
        params = {
            "state": "closed",
            "filter": "created",
            "pulls": "false",
            "per_page": self.PER_PAGE,
        }
        next_url = f"{self.GITHUB_API_URL}/{self.GITHUB_ROUTES.ISSUES}?{httpx.QueryParams(params)}"
        while next_url:
            response = await client.get(next_url)
            response.raise_for_status()
            json_data = response.json()
            if not json_data:
                logger.info("No more issues found.")
                break

            adapter = TypeAdapter(list[Issue])
            issues_page = adapter.validate_python(json_data)
            all_issues.extend(issues_page)

            if "link" in response.headers:
                links = {
                    part.split("; ")[1]: part.split("; ")[0].strip("<>")
                    for part in response.headers["link"].split(", ")
                }
                next_url = links.get('rel="next"')
            else:
                next_url = None

        return all_issues

    async def fetch_all_repositories(self, client: httpx.AsyncClient, username: str) -> list[Repository]:
        """
        Fetches all repositories for a user, handling API pagination.
        """

        all_repositories = []
        params = {
            "type": "all",
            "per_page": self.PER_PAGE,
        }
        next_url = (
            f"{self.GITHUB_API_URL}/"
            f"{self.GITHUB_ROUTES.USERS}/{username}/"
            f"{self.GITHUB_ROUTES.REPOSITORIES}"
            f"?{httpx.QueryParams(params)}"
        )

        while next_url:
            response = await client.get(next_url)
            response.raise_for_status()

            json_data = response.json()
            if not json_data:
                logger.info("No more repositories found.")
                break

            adapter = TypeAdapter(list[Repository])
            repositories_page = adapter.validate_python(json_data)
            all_repositories.extend(repositories_page)

            if "link" in response.headers:
                links = {
                    part.split("; ")[1]: part.split("; ")[0].strip("<>")
                    for part in response.headers["link"].split(", ")
                }
                next_url = links.get('rel="next"')
            else:
                next_url = None

        return all_repositories

    async def fetch_author_commits_for_repo(
        self, client: httpx.AsyncClient, repo_full_name: str, author: str, since_date: datetime | None
    ) -> list[RepoCommit]:
        """Fetch all commits for a given repository authored by the specified user."""
        all_repo_commits = []
        params = {
            "per_page": self.PER_PAGE,
            "author": author,
        }
        if since_date:
            logger.info("Fetching commits for repo '{}' by author '{}' since {}.", repo_full_name, author, since_date)
            params["since"] = since_date.isoformat()

        next_url = (
            f"{self.GITHUB_API_URL}/"
            f"{self.GITHUB_ROUTES.REPOSITORIES}/"
            f"{repo_full_name}/"
            f"{self.GITHUB_ROUTES.COMMITS}"
            f"?{httpx.QueryParams(params)}"
        )

        while next_url:
            response = await client.get(next_url)
            response.raise_for_status()
            json_data = response.json()

            if not json_data:
                logger.info("No more commits found for repository: {}", repo_full_name)
                break
            adapter = TypeAdapter(list[RepoCommit])
            all_repo_commits.extend(adapter.validate_python(response.json()))
            if "link" in response.headers:
                links = {
                    part.split("; ")[1]: part.split("; ")[0].strip("<>")
                    for part in response.headers["link"].split(", ")
                }

                next_url = links.get('rel="next"')

            else:
                next_url = None

        return all_repo_commits

    async def fetch_details_for_commits(
        self, client: httpx.AsyncClient, repo_commits: list[RepoCommit]
    ) -> list[Commit]:
        """Fetch detailed commit information for a list of lightweight commits."""

        tasks = []

        for repo_commit in repo_commits:
            tasks.append(self.fetch_with_semaphore(client, repo_commit))

        if not tasks:
            logger.info("No commit detail tasks to process.")
            return []

        results = await asyncio.gather(*tasks)

        return [commit for commit in results if commit is not None]

    async def fetch_commit_detail(
        self, client: httpx.AsyncClient, commit: Annotated[RepoCommit, "lightweight commit details"]
    ) -> Commit:
        """Helper to get a single commit's details and inject the repo_id."""
        url = commit.url
        response = await client.get(url)
        response.raise_for_status()

        adapter = TypeAdapter(Commit)
        commit_detail = adapter.validate_python(response.json())

        file_changes = [
            FileChange(filename=f.filename, additions=f.additions, deletions=f.deletions)
            for f in (commit_detail.files or [])
        ]

        analysis = self.analyzer_service.analyze_commit(message=commit_detail.commit.message, files=file_changes)

        commit_detail.significance_score = analysis.score
        commit_detail.significance_classification = analysis.classification

        return commit_detail

    async def fetch_with_semaphore(self, client: httpx.AsyncClient, commit: RepoCommit) -> Commit:
        """Wrapper to acquire semaphore before fetching."""
        # Create a semaphore to limit concurrency to 10 to avoid rate limits
        async with self.semaphore:
            if not commit.url:
                logger.warning("Commit URL is missing for commit SHA: {}", commit.sha)
                return None
            return await self.fetch_commit_detail(client, commit)

    async def get_commits_by_repo_id(self, repo_id: int) -> list[Commit]:
        """Fetch commits from the database for a given repository ID."""
        return await self.repo.get_commits_by_repo_id(repo_id)
