"""add_account_balances_and_transfers

Revision ID: d7e4b21908aa
Revises: c1f8a92e34d1
Create Date: 2026-10-26 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e4b21908aa'
down_revision = 'c1f8a92e34d1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('accounts', sa.Column('initial_balance', sa.Float(), server_default='0.0', nullable=False))
    op.add_column('expenses', sa.Column('destination_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_expenses_destination_account', 'expenses', 'accounts', ['destination_account_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_expenses_destination_account', 'expenses', type_='foreignkey')
    op.drop_column('expenses', 'destination_account_id')
    op.drop_column('accounts', 'initial_balance')
