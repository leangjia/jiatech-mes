"""Initial migration - create base tables.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    op.create_table(
        'res_company',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('currency_id', sa.Integer(), nullable=False),
        sa.Column('logo', sa.LargeBinary()),
        sa.Column('street', sa.String(length=255)),
        sa.Column('street2', sa.String(length=255)),
        sa.Column('city', sa.String(length=64)),
        sa.Column('state_id', sa.Integer()),
        sa.Column('country_id', sa.Integer()),
        sa.Column('zip', sa.String(length=8)),
        sa.Column('phone', sa.String(length=32)),
        sa.Column('email', sa.String(length=240)),
        sa.Column('website', sa.String(length=255)),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('sequence', sa.Integer(), nullable=False, default=10),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['partner_id'], ['res_partner.id']),
        sa.ForeignKeyConstraint(['currency_id'], ['res_currency.id']),
    )
    op.create_index('res_company_name_index', 'res_company', ['name'])
    
    op.create_table(
        'res_partner',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255)),
        sa.Column('ref', sa.String(length=64)),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('title', sa.Integer()),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('type', sa.String(length=16), default='contact'),
        sa.Column('street', sa.String(length=255)),
        sa.Column('street2', sa.String(length=255)),
        sa.Column('city', sa.String(length=64)),
        sa.Column('state_id', sa.Integer()),
        sa.Column('country_id', sa.Integer()),
        sa.Column('zip', sa.String(length=8)),
        sa.Column('phone', sa.String(length=32)),
        sa.Column('mobile', sa.String(length=32)),
        sa.Column('email', sa.String(length=240)),
        sa.Column('email_formatted', sa.String(length=255)),
        sa.Column('user_id', sa.Integer()),
        sa.Column('customer', sa.Boolean(), nullable=False, default=True),
        sa.Column('supplier', sa.Boolean(), nullable=False, default=False),
        sa.Column('employee', sa.Boolean(), nullable=False, default=False),
        sa.Column('function', sa.String(length=128)),
        sa.Column('comment', sa.Text()),
        sa.Column('website', sa.String(length=255)),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('res_partner_name_index', 'res_partner', ['name'])
    op.create_index('res_partner_ref_index', 'res_partner', ['ref'])
    op.create_index('res_partner_email_index', 'res_partner', ['email'])
    
    op.create_table(
        'res_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('login', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255)),
        sa.Column('email', sa.String(length=255)),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('lang', sa.String(length=8), default='en_US'),
        sa.Column('tz', sa.String(length=32), default='UTC'),
        sa.Column('login_date', sa.DateTime()),
        sa.Column('signature', sa.Text()),
        sa.Column('image_1920', sa.LargeBinary()),
        sa.Column('share', sa.Boolean(), nullable=False, default=False),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['res_company.id']),
    )
    op.create_index('res_users_login_index', 'res_users', ['login'])
    op.create_index('res_users_company_index', 'res_users', ['company_id'])
    
    op.create_table(
        'res_users_company_rel',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'company_id'),
        sa.ForeignKeyConstraint(['user_id'], ['res_users.id']),
        sa.ForeignKeyConstraint(['company_id'], ['res_company.id']),
    )
    
    op.create_table(
        'res_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('category_id', sa.Integer()),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('res_groups_name_index', 'res_groups', ['name'])
    
    op.create_table(
        'res_users_groups_rel',
        sa.Column('uid', sa.Integer(), nullable=False),
        sa.Column('gid', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('uid', 'gid'),
        sa.ForeignKeyConstraint(['uid'], ['res_users.id']),
        sa.ForeignKeyConstraint(['gid'], ['res_groups.id']),
    )
    
    op.create_table(
        'res_currency',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('symbol', sa.String(length=3), nullable=False),
        sa.Column('position', sa.String(length=1), default='after'),
        sa.Column('decimal_places', sa.Integer(), nullable=False, default=2),
        sa.Column('rounding', sa.Numeric(precision=3, scale=3), nullable=False, default=1.0),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('res_currency_name_index', 'res_currency', ['name'])
    
    op.create_table(
        'res_country',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False, unique=True),
        sa.Column('address_format', sa.Text()),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('res_country_code_index', 'res_country', ['code'])
    
    op.create_table(
        'res_country_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['country_id'], ['res_country.id']),
    )
    op.create_index('res_country_state_country_index', 'res_country_state', ['country_id'])
    
    op.create_table(
        'ir_sequence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False, unique=True),
        sa.Column('implementation', sa.String(length=8), default='standard'),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
        sa.Column('prefix', sa.String(length=64)),
        sa.Column('suffix', sa.String(length=64)),
        sa.Column('padding', sa.Integer(), nullable=False, default=6),
        sa.Column('number_next', sa.Integer(), nullable=False, default=1),
        sa.Column('number_next_actual', sa.Integer(), nullable=False, default=1),
        sa.Column('create_uid', sa.Integer()),
        sa.Column('create_date', sa.DateTime()),
        sa.Column('write_uid', sa.Integer()),
        sa.Column('write_date', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ir_sequence_code_index', 'ir_sequence', ['code'])


def downgrade() -> None:
    op.drop_table('ir_sequence')
    op.drop_table('res_country_state')
    op.drop_table('res_country')
    op.drop_table('res_currency')
    op.drop_table('res_users_groups_rel')
    op.drop_table('res_groups')
    op.drop_table('res_users_company_rel')
    op.drop_table('res_users')
    op.drop_table('res_partner')
    op.drop_table('res_company')
