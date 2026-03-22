"""WIP module tables migration.

Revision ID: 002_wip
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002_wip'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mes_route',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False, unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_route_code_index', 'mes_route', ['code'])
    
    op.create_table(
        'mes_workcenter',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False, unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('capacity_per_cycle', sa.Float(), default=1.0),
        sa.Column('time_cycle', sa.Float(), default=0.0),
        sa.Column('time_efficiency', sa.Float(), default=100.0),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_workcenter_code_index', 'mes_workcenter', ['code'])
    
    op.create_table(
        'mes_route_operation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False, default=10),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('workcenter_id', sa.Integer()),
        sa.Column('time_cycle', sa.Float(), default=0.0),
        sa.Column('time_efficiency', sa.Float(), default=100.0),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['route_id'], ['mes_route.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workcenter_id'], ['mes_workcenter.id']),
    )
    op.create_index('mes_route_operation_route_index', 'mes_route_operation', ['route_id'])
    op.create_index('mes_route_operation_sequence_index', 'mes_route_operation', ['route_id', 'sequence'])
    
    op.create_table(
        'mes_team',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('leader_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'mes_resource',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), unique=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('resource_type', sa.String(length=16), default='user'),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'mes_lot',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=16), nullable=False, default='pending'),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('bom_id', sa.Integer()),
        sa.Column('route_id', sa.Integer()),
        sa.Column('quantity', sa.Float(), nullable=False, default=1.0),
        sa.Column('uom_id', sa.Integer()),
        sa.Column('product_qty', sa.Float(), nullable=False, default=1.0),
        sa.Column('material_qty', sa.Float(), default=0.0),
        sa.Column('progress', sa.Float(), default=0.0),
        sa.Column('company_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_lot_name_index', 'mes_lot', ['name'])
    op.create_index('mes_lot_state_index', 'mes_lot', ['state'])
    op.create_index('mes_lot_product_index', 'mes_lot', ['product_id'])
    
    op.create_table(
        'mes_workorder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('lot_id', sa.Integer(), nullable=False),
        sa.Column('operation_id', sa.Integer()),
        sa.Column('workcenter_id', sa.Integer()),
        sa.Column('team_id', sa.Integer()),
        sa.Column('state', sa.String(length=16), nullable=False, default='pending'),
        sa.Column('sequence', sa.Integer(), default=0),
        sa.Column('planned_start', sa.DateTime()),
        sa.Column('planned_end', sa.DateTime()),
        sa.Column('actual_start', sa.DateTime()),
        sa.Column('actual_end', sa.DateTime()),
        sa.Column('planned_qty', sa.Float(), default=0.0),
        sa.Column('done_qty', sa.Float(), default=0.0),
        sa.Column('rejected_qty', sa.Float(), default=0.0),
        sa.Column('progress', sa.Float(), default=0.0),
        sa.Column('company_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lot_id'], ['mes_lot.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operation_id'], ['mes_route_operation.id']),
        sa.ForeignKeyConstraint(['workcenter_id'], ['mes_workcenter.id']),
    )
    op.create_index('mes_workorder_lot_index', 'mes_workorder', ['lot_id'])
    op.create_index('mes_workorder_state_index', 'mes_workorder', ['state'])


def downgrade() -> None:
    op.drop_table('mes_workorder')
    op.drop_table('mes_lot')
    op.drop_table('mes_resource')
    op.drop_table('mes_team')
    op.drop_table('mes_route_operation')
    op.drop_table('mes_workcenter')
    op.drop_table('mes_route')
