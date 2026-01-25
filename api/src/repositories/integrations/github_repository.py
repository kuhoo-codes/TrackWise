from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Errors, settings
from src.core.redis_utils import redis_get, redis_set
from src.exceptions.external import GitHubIntegrationError
from src.models.integrations.github import GithubCommit, GithubIssue
from src.models.integrations.github import GithubRepository as GithubRepositoryModel
from src.schemas.integrations.github import Commit, GithubToken, Issue, Repository, StateRecord


class GithubRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.state_store: dict[str, StateRecord] = {}
        self.token_store: dict[str, GithubToken] = {}
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.db = db

    async def save_state(
        self, state: Annotated[str, "GitHub OAuth state parameter"], user_id: Annotated[str, "Associated user ID"]
    ) -> None:
        """Save GitHub OAuth `state` mapping to user_id in Redis for validation."""
        record = StateRecord(user_id=user_id, created_at=datetime.now())
        key = f"github:state:{state}"
        redis_set(key, record, ex=self.access_token_expire_minutes * 60)

    async def validate_state(self, state: Annotated[str, "GitHub OAuth state parameter to validate"]) -> StateRecord:
        """Validate a stored GitHub OAuth state and return its record."""
        key = f"github:state:{state}"
        record = redis_get(key, model=StateRecord)

        if not record:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": "Invalid state parameter"}
            )

        if record.used:
            raise GitHubIntegrationError(Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": "State already used"})
        record.used = True
        redis_set(key, record)

        return record

    async def save_token(
        self,
        user_id: Annotated[str, "User ID associated with GitHub token"],
        token: Annotated[GithubToken, "GitHub OAuth access token data"],
    ) -> None:
        """Store a GitHub access token for a user in Redis."""
        key = f"github:token:{user_id}"

        self.token_store[key] = token

        redis_set(key, token.model_dump_json(), ex=token.expires_in)

        return token

    async def get_token(self, user_id: Annotated[str, "User ID to retrieve token for"]) -> GithubToken:
        """Retrieve a GitHub access token for a given user from Redis."""
        key = f"github:token:{user_id}"
        token = redis_get(key, model=GithubToken)
        if not token:
            raise GitHubIntegrationError(
                Errors.GITHUB_INTEGRATION_ERROR.value, details={"error": "GitHub token not found"}
            )
        return token

    async def get_commits_by_repo_id(self, repo_id: int) -> list[GithubCommit]:
        """Fetch commits from the database for a given repository ID."""
        stmt = select(GithubCommit).where(GithubCommit.repository_id == repo_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def bulk_upsert_repositories(
        self, repos_data: list[Repository], external_profile_id: Annotated[int, "Foreign key to ExternalProfile"]
    ) -> list[GithubRepositoryModel]:
        """
        Bulk insert or update repository data in a single call.

        If a repo already exists, it will be updated; otherwise, a new record will be inserted.
        """
        if not repos_data:
            return []

        insert_values = [
            {
                "external_profile_id": external_profile_id,
                "github_repo_id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "html_url": repo.html_url,
                "language": repo.language,
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "is_fork": repo.fork,
                "repo_created_at": repo.created_at,
                "repo_updated_at": repo.updated_at,
            }
            for repo in repos_data
        ]

        stmt = insert(GithubRepositoryModel)

        stmt = stmt.on_conflict_do_update(
            index_elements=[GithubRepositoryModel.github_repo_id],
            set_={
                "name": stmt.excluded.name,
                "description": stmt.excluded.description,
                "language": stmt.excluded.language,
                "stargazers_count": stmt.excluded.stargazers_count,
                "forks_count": stmt.excluded.forks_count,
                "repo_updated_at": stmt.excluded.repo_updated_at,
            },
        ).returning(GithubRepositoryModel)

        result = await self.db.execute(stmt, insert_values)
        await self.db.commit()
        return result.scalars().all()

    async def bulk_upsert_issues(
        self,
        issue_data: list[Issue],
        external_profile_id: Annotated[int, "Foreign key to ExternalProfile"],
        repo_id_map: Annotated[dict[str, int], "Mapping of GitHub repo full_name → DB ID"],
    ) -> list[GithubIssue]:
        """Performs a bulk insert/update for a list of issues."""
        if not issue_data:
            return []

        insert_values = []
        for issue in issue_data:
            repo_full_name = issue.repository_url.split("https://api.github.com/repos/")[-1]
            repo_db_id = repo_id_map.get(repo_full_name)

            if repo_db_id:
                insert_values.append(
                    {
                        "external_profile_id": external_profile_id,
                        "repository_id": repo_db_id,
                        "github_issue_id": issue.id,
                        "number": issue.number,
                        "state": issue.state,
                        "title": issue.title,
                        "body": issue.body,
                        "html_url": issue.html_url,
                        "issue_created_at": issue.created_at,
                        "issue_closed_at": issue.closed_at,
                    }
                )

        if not insert_values:
            return []

        stmt = insert(GithubIssue).values(insert_values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[GithubIssue.github_issue_id],
            set_={
                "state": stmt.excluded.state,
                "title": stmt.excluded.title,
                "body": stmt.excluded.body,
                "issue_closed_at": stmt.excluded.issue_closed_at,
            },
        ).returning(GithubIssue)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalars().all()

    async def bulk_upsert_commit_details(
        self,
        commit_data_list: list[Commit],
        external_profile_id: Annotated[int, "Foreign key to ExternalProfile"],
        repo_db_id: Annotated[int, "Foreign key to GithubRepository"],
    ) -> list[GithubCommit]:
        """Bulk insert or update commit details efficiently in one query."""
        if not commit_data_list:
            return []

        insert_values = []
        for commit in commit_data_list:
            files_json = [file.model_dump() for file in commit.files]
            authored_date = commit.commit.author.date if commit.commit.author else datetime.now(timezone.utc)

            insert_values.append(
                {
                    "sha": commit.sha,
                    "external_profile_id": external_profile_id,
                    "repository_id": repo_db_id,
                    "author_id": commit.author.id if commit.author else 0,
                    "message": commit.commit.message,
                    "authored_at": authored_date,
                    "html_url": commit.html_url,
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                    "total": commit.stats.total,
                    "files": files_json,
                    "significance_score": commit.significance_score,
                    "significance_classification": commit.significance_classification,
                }
            )

        stmt = insert(GithubCommit)

        stmt = stmt.on_conflict_do_update(
            index_elements=[GithubCommit.sha],
            set_={
                "message": stmt.excluded.message,
                "authored_at": stmt.excluded.authored_at,
                "additions": stmt.excluded.additions,
                "deletions": stmt.excluded.deletions,
                "total": stmt.excluded.total,
                "files": stmt.excluded.files,
            },
        ).returning(GithubCommit)

        result = await self.db.execute(stmt, insert_values)
        await self.db.commit()
        return result.scalars().all()

    async def update_repo_sync_time(self, repo_db_id: int) -> None:
        """Updates the 'last_commit_sync_at' for a repository."""
        stmt = (
            update(GithubRepositoryModel)
            .where(GithubRepositoryModel.id == repo_db_id)
            .values(last_commit_sync_at=datetime.now(timezone.utc))
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_db_repositories(
        self, external_profile_id: Annotated[int, "Foreign key to ExternalProfile"]
    ) -> list[GithubRepositoryModel]:
        """Fetch all GitHub repositories for an external profile from the database."""
        stmt = select(GithubRepositoryModel).where(GithubRepositoryModel.external_profile_id == external_profile_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
