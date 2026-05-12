"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("payment_id", sa.String(64), nullable=False, unique=True),
        sa.Column("state_key", sa.String(128), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("currency_from", sa.String(3), nullable=False),
        sa.Column("currency_to", sa.String(3), nullable=False),
        sa.Column("sender_country", sa.String(3), nullable=False),
        sa.Column("receiver_country", sa.String(3), nullable=False),
        sa.Column("sender_name", sa.String(140), nullable=False),
        sa.Column("receiver_name", sa.String(140), nullable=False),
        sa.Column("payment_purpose", sa.String(280), nullable=True),
        sa.Column("routing_preference", sa.String(20), nullable=True, server_default="balanced"),
        sa.Column("compliance_status", sa.String(30), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("selected_rail", sa.String(40), nullable=True),
        sa.Column("execution_status", sa.String(30), nullable=True),
        sa.Column("execution_time", sa.Float(), nullable=True),
        sa.Column("actual_cost", sa.Float(), nullable=True),
        sa.Column("actual_processing_time", sa.Float(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.text("now()")),
    )

    op.create_table(
        "payment_audit_log",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("payment_id", sa.String(64), sa.ForeignKey("payments.payment_id"), nullable=False),
        sa.Column("stage", sa.String(40), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "compliance_decisions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("payment_id", sa.String(64), sa.ForeignKey("payments.payment_id"), nullable=False),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("officer_id", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("compliance_decisions")
    op.drop_table("payment_audit_log")
    op.drop_table("payments")
