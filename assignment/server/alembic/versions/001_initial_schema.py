"""
    Initial Schema for discovery jobs and leads
    Revision ID: 001_initial_schema
    Revises:
        Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # create discovery jobs table
    op.create_table(
        "discovery_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('business_description', sa.String(), nullable=False),
        sa.Column('target_market', sa.String(2), nullable=False),
        sa.Column('buyer_types', JSON, nullable=False),
        sa.Column('max_results', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )

    # create discovery leads table
    op.create_table(
        'discovery_leads',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('job_id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('headquarters_city', sa.String(), nullable=False),
        sa.Column('fit_score', sa.Float(), nullable=False),
        sa.Column('justification', sa.String(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
    )

    op.create_foreign_key(
        "fk_discovery_leads_job_id",
        "discovery_leads", "discovery_jobs",
        ["job_id"], ["id"],
        ondelete="CASCADE"
    )

    op.create_index('ix_discovery_jobs_status', 'discovery_jobs', ['status'])
    op.create_index('ix_discovery_leads_job_id', 'discovery_leads', ['job_id'])
    op.create_index('ix_discovery_leads_rank', 'discovery_leads', ['rank'])

def downgrade():
    op.drop_table("discovery_leads")
    op.drop_table("discovery_jobs")