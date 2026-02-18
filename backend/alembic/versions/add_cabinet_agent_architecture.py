"""Add Cabinet, Agent, and multi-societe architecture

Revision ID: add_cabinet_agent_v1
Revises: 5faca5342953
Create Date: 2026-02-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cabinet_agent_v1'
down_revision = '5faca5342953'
branch_labels = None
depends_on = None


def upgrade():
    # Create Cabinet table
    op.create_table(
        'cabinets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telephone', sa.String(20), nullable=True),
        sa.Column('adresse', sa.String(500), nullable=True),
        sa.Column('logo_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cabinets_nom'), 'cabinets', ['nom'], unique=True)
    
    # Create Agent table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cabinet_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(500), nullable=False),
        sa.Column('nom', sa.String(255), nullable=True),
        sa.Column('prenom', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['cabinet_id'], ['cabinets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_cabinet_id'), 'agents', ['cabinet_id'])
    op.create_index(op.f('ix_agents_username'), 'agents', ['username'], unique=True)
    op.create_index(op.f('ix_agents_email'), 'agents', ['email'], unique=True)
    
    # Modify societes table: add cabinet_id, logo_path, patente
    op.add_column('societes', sa.Column('cabinet_id', sa.Integer(), nullable=True))
    op.add_column('societes', sa.Column('logo_path', sa.String(500), nullable=True))
    op.add_column('societes', sa.Column('patente', sa.String(50), nullable=True))
    op.add_column('societes', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    
    # Set existing societes to cabinet_id = 1 (will need manual fix or seed)
    op.execute("UPDATE societes SET cabinet_id = 1 WHERE cabinet_id IS NULL")
    
    # Make cabinet_id NOT NULL after setting values
    op.alter_column('societes', 'cabinet_id', existing_type=sa.Integer(), nullable=False)
    
    # Create foreign key for cabinet_id
    op.create_foreign_key('fk_societes_cabinet_id', 'societes', 'cabinets', ['cabinet_id'], ['id'])
    op.create_index(op.f('ix_societes_cabinet_id'), 'societes', ['cabinet_id'])
    
    # Create Many-to-Many table: agent_societes
    op.create_table(
        'agent_societes',
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('societe_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['societe_id'], ['societes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('agent_id', 'societe_id')
    )
    op.create_index(op.f('ix_agent_societes_agent_id'), 'agent_societes', ['agent_id'])
    op.create_index(op.f('ix_agent_societes_societe_id'), 'agent_societes', ['societe_id'])
    
    # Create CompteurFacturation table
    op.create_table(
        'compteurs_facturation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('societe_id', sa.Integer(), nullable=False),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('dernier_numero', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['societe_id'], ['societes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compteurs_facturation_societe_id'), 'compteurs_facturation', ['societe_id'])
    op.create_unique_constraint('uq_compteur_societe_annee', 'compteurs_facturation', ['societe_id', 'annee'])


def downgrade():
    # Reverse order: drop new constraints first, then tables
    op.drop_constraint('uq_compteur_societe_annee', 'compteurs_facturation', type_='unique')
    op.drop_index(op.f('ix_compteurs_facturation_societe_id'), 'compteurs_facturation')
    op.drop_table('compteurs_facturation')
    
    op.drop_index(op.f('ix_agent_societes_societe_id'), 'agent_societes')
    op.drop_index(op.f('ix_agent_societes_agent_id'), 'agent_societes')
    op.drop_table('agent_societes')
    
    op.drop_index(op.f('ix_societes_cabinet_id'), 'societes')
    op.drop_constraint('fk_societes_cabinet_id', 'societes', type_='foreignkey')
    op.drop_column('societes', 'updated_at')
    op.drop_column('societes', 'patente')
    op.drop_column('societes', 'logo_path')
    op.drop_column('societes', 'cabinet_id')
    
    op.drop_index(op.f('ix_agents_email'), 'agents')
    op.drop_index(op.f('ix_agents_username'), 'agents')
    op.drop_index(op.f('ix_agents_cabinet_id'), 'agents')
    op.drop_table('agents')
    
    op.drop_index(op.f('ix_cabinets_nom'), 'cabinets')
    op.drop_table('cabinets')
