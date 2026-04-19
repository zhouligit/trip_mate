"""friendships table and groups.invite_code

Revision ID: 20260415_0003
Revises: 20260414_0002
Create Date: 2026-04-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0003"
down_revision = "20260414_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("invite_code", sa.String(length=32), nullable=True))
    op.create_index("uk_groups_invite_code", "groups", ["invite_code"], unique=True)

    op.create_table(
        "friendships",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("friend_user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["friend_user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id", "friend_user_id", name="uk_user_friend"),
    )
    op.create_index("idx_friendships_user_id", "friendships", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_friendships_user_id", table_name="friendships")
    op.drop_table("friendships")
    op.drop_index("uk_groups_invite_code", table_name="groups")
    op.drop_column("groups", "invite_code")
