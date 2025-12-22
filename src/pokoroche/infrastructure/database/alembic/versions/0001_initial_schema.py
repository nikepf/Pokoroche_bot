from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("telegram_message_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=True),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_messages_user_id_users",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_messages_telegram_message_id", "messages", ["telegram_message_id"], unique=False)
    op.create_index("ix_messages_chat_id", "messages", ["chat_id"], unique=False)
    op.create_index("ix_messages_user_id", "messages", ["user_id"], unique=False)

    op.create_table(
        "digests",
        sa.Column("id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("important_messages", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("feedback_score", sa.Float(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_digests_user_id_users",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_digests_user_id", "digests", ["user_id"], unique=False)
    op.create_index("ix_digests_sent_at", "digests", ["sent_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_digests_sent_at", table_name="digests")
    op.drop_index("ix_digests_user_id", table_name="digests")
    op.drop_table("digests")

    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_index("ix_messages_chat_id", table_name="messages")
    op.drop_index("ix_messages_telegram_message_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
