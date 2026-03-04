"""Add fields in GithubRepository

Revision ID: 5cf71efa231f
Revises: deb06b345f2b
Create Date: 2026-03-01 21:47:36.108661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # <-- Add this import

# revision identifiers, used by Alembic.
revision: str = '5cf71efa231f'
down_revision: Union[str, None] = 'deb06b345f2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    generation_status_enum = postgresql.ENUM('IDLE', 'GENERATING', 'COMPLETED', 'FAILED', name='generationstatusenum')
    generation_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('github_repositories', sa.Column(
        'generation_status', 
        sa.Enum('IDLE', 'GENERATING', 'COMPLETED', 'FAILED', name='generationstatusenum'), 
        nullable=False, 
        server_default='IDLE'
    ))
    
    op.add_column('github_repositories', sa.Column('last_generation_attempt_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('github_repositories', sa.Column('last_generation_error', sa.String(), nullable=True))
    op.create_index(op.f('ix_github_repositories_generation_status'), 'github_repositories', ['generation_status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_github_repositories_generation_status'), table_name='github_repositories')
    op.drop_column('github_repositories', 'last_generation_error')
    op.drop_column('github_repositories', 'last_generation_attempt_at')
    op.drop_column('github_repositories', 'generation_status')
    
    generation_status_enum = postgresql.ENUM('IDLE', 'GENERATING', 'COMPLETED', 'FAILED', name='generationstatusenum')
    generation_status_enum.drop(op.get_bind(), checkfirst=True)