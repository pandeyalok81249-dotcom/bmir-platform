"""add_subscriptions_and_composite_indexes

Revision ID: c5a89e1b2345
Revises: 8c99c13b2b4b
Create Date: 2026-11-04 01:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a89e1b2345'
down_revision: Union[str, Sequence[str], None] = '8c99c13b2b4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create user_subscriptions table
    op.create_table(
        'user_subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('tier', sa.String(length=50), nullable=False, server_default='free'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_user_subscriptions_id', 'user_subscriptions', ['id'], unique=False)
    op.create_index('ix_user_subscriptions_user_id', 'user_subscriptions', ['user_id'], unique=False)
    op.create_index('ix_subscriptions_user_status', 'user_subscriptions', ['user_id', 'status'], unique=False)

    # 2. Create user_usage_quotas table
    op.create_table(
        'user_usage_quotas',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('month_period', sa.String(length=7), nullable=False),
        sa.Column('resumes_uploaded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ai_analyses_run', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('interviews_conducted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('simulations_run', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_user_usage_quotas_id', 'user_usage_quotas', ['id'], unique=False)
    op.create_index('ix_user_usage_quotas_user_id', 'user_usage_quotas', ['user_id'], unique=False)

    # 3. Add composite performance indexes
    op.create_index('ix_resumes_user_created', 'resumes', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_analyses_resume_created', 'resume_analyses', ['resume_id', 'created_at'], unique=False)
    op.create_index('ix_job_matches_version_score', 'job_matches', ['resume_version_id', 'match_score'], unique=False)
    op.create_index('ix_interviews_user_created', 'interview_sessions', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_interviews_user_created', table_name='interview_sessions')
    op.drop_index('ix_job_matches_version_score', table_name='job_matches')
    op.drop_index('ix_analyses_resume_created', table_name='resume_analyses')
    op.drop_index('ix_resumes_user_created', table_name='resumes')

    op.drop_index('ix_user_usage_quotas_user_id', table_name='user_usage_quotas')
    op.drop_index('ix_user_usage_quotas_id', table_name='user_usage_quotas')
    op.drop_table('user_usage_quotas')

    op.drop_index('ix_subscriptions_user_status', table_name='user_subscriptions')
    op.drop_index('ix_user_subscriptions_user_id', table_name='user_subscriptions')
    op.drop_index('ix_user_subscriptions_id', table_name='user_subscriptions')
    op.drop_table('user_subscriptions')
