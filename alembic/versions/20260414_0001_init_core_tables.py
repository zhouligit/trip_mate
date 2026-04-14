"""init core tables for mvp

Revision ID: 20260414_0001
Revises:
Create Date: 2026-04-14 12:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260414_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("wechat_openid", sa.String(length=64), nullable=False),
        sa.Column("unionid", sa.String(length=64), nullable=True),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("mobile", sa.String(length=20), nullable=True),
        sa.Column("realname_verified", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("wechat_openid", name="uk_users_openid"),
    )

    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("city_code", sa.String(length=32), nullable=False),
        sa.Column("district_code", sa.String(length=32), nullable=True),
        sa.Column("tags_json", sa.JSON(), nullable=False),
        sa.Column("personality_test_done", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("trust_score", sa.Integer(), nullable=False, server_default="100"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "groups",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("city_code", sa.String(length=32), nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("threshold_count", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("vote_deadline", sa.DateTime(), nullable=True),
        sa.Column("group_deadline", sa.DateTime(), nullable=True),
        sa.Column("trip_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )
    op.create_index("idx_groups_status_city", "groups", ["status", "city_code"])

    op.create_table(
        "group_members",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="member"),
        sa.Column("pay_status", sa.String(length=16), nullable=False, server_default="unpaid"),
        sa.Column("join_status", sa.String(length=16), nullable=False, server_default="joined"),
        sa.Column("joined_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("group_id", "user_id", name="uk_group_user"),
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("is_valid", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("winner_option_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
    )

    op.create_table(
        "vote_options",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("vote_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("route_desc", sa.String(length=255), nullable=False),
        sa.Column("duration_desc", sa.String(length=64), nullable=False),
        sa.Column("meetup_points_json", sa.JSON(), nullable=False),
        sa.Column("fee_estimate", sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(["vote_id"], ["votes.id"]),
    )

    op.create_table(
        "vote_records",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("vote_id", sa.BigInteger(), nullable=False),
        sa.Column("option_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["vote_id"], ["votes.id"]),
        sa.ForeignKeyConstraint(["option_id"], ["vote_options.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("vote_id", "user_id", name="uk_vote_user"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("platform_fee", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("insurance_fee", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="unpaid"),
        sa.Column("pay_deadline", sa.DateTime(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.UniqueConstraint("order_no", name="uk_order_no"),
    )
    op.create_index("idx_orders_user_status", "orders", ["user_id", "status"])

    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("out_trade_no", sa.String(length=64), nullable=False),
        sa.Column("wechat_txn_id", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("notify_raw", sa.JSON(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.UniqueConstraint("out_trade_no", name="uk_out_trade_no"),
    )


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_index("idx_orders_user_status", table_name="orders")
    op.drop_table("orders")
    op.drop_table("vote_records")
    op.drop_table("vote_options")
    op.drop_table("votes")
    op.drop_table("group_members")
    op.drop_index("idx_groups_status_city", table_name="groups")
    op.drop_table("groups")
    op.drop_table("user_profiles")
    op.drop_table("users")
