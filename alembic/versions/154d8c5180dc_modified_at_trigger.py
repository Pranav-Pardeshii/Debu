"""modified at trigger

Revision ID: 154d8c5180dc
Revises: d1d3c191b89e
Create Date: 2026-10-01 13:46:14.223449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '154d8c5180dc'
down_revision: Union[str, Sequence[str], None] = 'd1d3c191b89e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION update_debate_modified_at()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE debates
            SET modified_at = NOW()
            WHERE debate_id = NEW.debate_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER set_debate_modified_at
        AFTER INSERT ON messages
        FOR EACH ROW
        EXECUTE FUNCTION update_debate_modified_at();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_debate_modified_at ON messages;")
    op.execute("DROP FUNCTION IF EXISTS update_debate_modified_at;")