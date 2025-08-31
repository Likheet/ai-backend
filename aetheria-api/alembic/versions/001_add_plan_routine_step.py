"""add_plan_routine_step_tables

Revision ID: 001_add_plan_routine_step
Revises: 
Create Date: 2025-09-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '001_add_plan_routine_step'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade to this revision."""
    
    # Create plan table
    op.execute("""
        CREATE TABLE IF NOT EXISTS plan (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID NOT NULL UNIQUE REFERENCES assessment_session(id) ON DELETE CASCADE,
            skin_profile JSONB NOT NULL,
            rationale JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    
    # Create unique index on session_id
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_plan_session_id 
        ON plan(session_id)
    """)
    
    # Create routine_step table
    op.execute("""
        CREATE TABLE IF NOT EXISTS routine_step (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            plan_id UUID NOT NULL REFERENCES plan(id) ON DELETE CASCADE,
            "when" TEXT NOT NULL CHECK ("when" IN ('AM', 'PM')),
            step_order INTEGER NOT NULL,
            product_id UUID NULL,
            instructions TEXT NOT NULL,
            day_of_week INTEGER NULL CHECK (day_of_week BETWEEN 0 AND 6)
        )
    """)
    
    # Create composite index on plan_id, when, step_order
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_routine_step_plan_when_order 
        ON routine_step(plan_id, "when", step_order)
    """)


def downgrade() -> None:
    """Downgrade from this revision."""
    
    # Drop indexes first
    op.execute('DROP INDEX IF EXISTS ix_routine_step_plan_when_order')
    op.execute('DROP INDEX IF EXISTS ix_plan_session_id')
    
    # Drop tables (routine_step first due to foreign key)
    op.execute('DROP TABLE IF EXISTS routine_step')
    op.execute('DROP TABLE IF EXISTS plan')
