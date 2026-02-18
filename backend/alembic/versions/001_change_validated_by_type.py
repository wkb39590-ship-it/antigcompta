"""Change validated_by from INTEGER to VARCHAR

Revision ID: 001_change_validated_by
Revises: 5faca5342953
Create Date: 2026-02-18 16:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_change_validated_by'
down_revision = '5faca5342953'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Changer le type de validated_by dans la table factures
    op.alter_column('factures', 'validated_by',
               existing_type=sa.Integer(),
               type_=sa.String(255),
               nullable=True)
    
    # Changer le type de validated_by dans la table journal_entries
    op.alter_column('journal_entries', 'validated_by',
               existing_type=sa.Integer(),
               type_=sa.String(255),
               nullable=True)


def downgrade() -> None:
    # Revenir aux types Integer
    op.alter_column('factures', 'validated_by',
               existing_type=sa.String(255),
               type_=sa.Integer(),
               nullable=True)
    
    op.alter_column('journal_entries', 'validated_by',
               existing_type=sa.String(255),
               type_=sa.Integer(),
               nullable=True)
