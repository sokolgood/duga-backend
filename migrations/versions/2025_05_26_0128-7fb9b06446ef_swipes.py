"""Swipes

Revision ID: 7fb9b06446ef
Revises: 41a4eccae865
Create Date: 2025-05-26 01:28:37.681070

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7fb9b06446ef"
down_revision: str | None = "41a4eccae865"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


swipe_action_enum = sa.Enum("LIKE", "DISLIKE", "HIDE", name="swipeaction")


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type first
    swipe_action_enum.create(op.get_bind(), checkfirst=True)

    # Then use it in the column
    op.add_column("swipes", sa.Column("action", swipe_action_enum, nullable=False))
    op.drop_column("swipes", "liked")


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the old column
    op.add_column("swipes", sa.Column("liked", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column("swipes", "action")

    # Drop the enum type
    swipe_action_enum.drop(op.get_bind(), checkfirst=True)
