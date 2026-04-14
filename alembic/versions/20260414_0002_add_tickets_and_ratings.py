"""add tickets and ratings tables

Revision ID: 20260414_0002
Revises: 20260414_0001
Create Date: 2026-04-14 20:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0002"
down_revision = "20260414_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("ticket_no", sa.String(length=64), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("qr_code", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="issued"),
        sa.Column("verify_time", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.UniqueConstraint("ticket_no", name="uk_ticket_no"),
    )
    op.create_index("idx_tickets_group_user", "tickets", ["group_id", "user_id"])
    op.create_index("idx_tickets_qr_code", "tickets", ["qr_code"], unique=True)

    op.create_table(
        "ratings",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("mate_score", sa.SmallInteger(), nullable=False),
        sa.Column("route_score", sa.SmallInteger(), nullable=False),
        sa.Column("bus_score", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("group_id", "user_id", name="uk_group_user_rating"),
    )
    op.create_index("idx_ratings_group", "ratings", ["group_id"])


def downgrade() -> None:
    op.drop_index("idx_ratings_group", table_name="ratings")
    op.drop_table("ratings")
    op.drop_index("idx_tickets_qr_code", table_name="tickets")
    op.drop_index("idx_tickets_group_user", table_name="tickets")
    op.drop_table("tickets")
