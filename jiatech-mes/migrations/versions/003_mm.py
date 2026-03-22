"""MM module tables migration.

Revision ID: 003_mm
Revises: 002_wip
Create Date: 2024-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '003_mm'
down_revision: Union[str, None] = '002_wip'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mes_uom',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=8), nullable=False, unique=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('factor', sa.Float(), nullable=False, default=1.0),
        sa.Column('factor_inv', sa.Float()),
        sa.Column('rounding', sa.Float(), nullable=False, default=0.01),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('uom_type', sa.String(length=16), default='unit'),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_uom_code_index', 'mes_uom', ['code'])
    
    op.create_table(
        'mes_uom_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    
    op.create_table(
        'mes_product_category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('code', sa.String(length=16)),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_product_category_parent_index', 'mes_product_category', ['parent_id'])
    
    op.create_table(
        'mes_product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32), unique=True),
        sa.Column('type', sa.String(length=16), nullable=False, default='stockable'),
        sa.Column('tracking', sa.String(length=16), default='none'),
        sa.Column('categ_id', sa.Integer()),
        sa.Column('uom_id', sa.Integer(), nullable=False),
        sa.Column('uom_po_id', sa.Integer()),
        sa.Column('list_price', sa.Float(), default=0.0),
        sa.Column('standard_price', sa.Float(), default=0.0),
        sa.Column('volume', sa.Float()),
        sa.Column('weight', sa.Float()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_product_code_index', 'mes_product', ['code'])
    op.create_index('mes_product_categ_index', 'mes_product', ['categ_id'])
    
    op.create_table(
        'mes_bom',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_tmpl_id', sa.Integer()),
        sa.Column('product_qty', sa.Float(), nullable=False, default=1.0),
        sa.Column('product_uom_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=32)),
        sa.Column('type', sa.String(length=16), default='normal'),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_bom_product_index', 'mes_bom', ['product_id'])
    op.create_index('mes_bom_code_index', 'mes_bom', ['code'])
    
    op.create_table(
        'mes_bom_line',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bom_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_qty', sa.Float(), nullable=False, default=1.0),
        sa.Column('product_uom_id', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), default=1),
        sa.Column('factor', sa.Float(), default=1.0),
        sa.Column('bom_id', sa.Integer()),
        sa.Column('route_ids', sa.Text()),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['bom_id'], ['mes_bom.id'], ondelete='CASCADE'),
    )
    op.create_index('mes_bom_line_bom_index', 'mes_bom_line', ['bom_id'])
    op.create_index('mes_bom_line_product_index', 'mes_bom_line', ['product_id'])
    
    op.create_table(
        'mes_stock_location',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=32)),
        sa.Column('complete_name', sa.String(length=512)),
        sa.Column('location_type', sa.String(length=16), nullable=False, default='internal'),
        sa.Column('usage', sa.String(length=16), nullable=False, default='internal'),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('parent_path', sa.String(length=512)),
        sa.Column('company_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_stock_location_parent_index', 'mes_stock_location', ['parent_id'])
    
    op.create_table(
        'mes_stock_quant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('reserved_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('lot_id', sa.Integer()),
        sa.Column('package_id', sa.Integer()),
        sa.Column('owner_id', sa.Integer()),
        sa.Column('company_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_stock_quant_product_index', 'mes_stock_quant', ['product_id'])
    op.create_index('mes_stock_quant_location_index', 'mes_stock_quant', ['location_id'])
    
    op.create_table(
        'mes_stock_move',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_uom', sa.Integer(), nullable=False),
        sa.Column('product_uom_qty', sa.Float(), nullable=False, default=0.0),
        sa.Column('quantity_done', sa.Float(), default=0.0),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('location_dest_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(length=16), nullable=False, default='draft'),
        sa.Column('picking_id', sa.Integer()),
        sa.Column('origin', sa.String(length=255)),
        sa.Column('procurement_id', sa.Integer()),
        sa.Column('group_id', sa.Integer()),
        sa.Column('rule_id', sa.Integer()),
        sa.Column('company_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('mes_stock_move_product_index', 'mes_stock_move', ['product_id'])
    op.create_index('mes_stock_move_location_index', 'mes_stock_move', ['location_id'])
    op.create_index('mes_stock_move_state_index', 'mes_stock_move', ['state'])


def downgrade() -> None:
    op.drop_table('mes_stock_move')
    op.drop_table('mes_stock_quant')
    op.drop_table('mes_stock_location')
    op.drop_table('mes_bom_line')
    op.drop_table('mes_bom')
    op.drop_table('mes_product')
    op.drop_table('mes_product_category')
    op.drop_table('mes_uom_category')
    op.drop_table('mes_uom')
