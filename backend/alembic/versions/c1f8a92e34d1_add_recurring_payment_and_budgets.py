"""add_recurring_payment_and_budgets

Revision ID: c1f8a92e34d1
Revises: 195a8571f735
Create Date: 2026-10-26 20:36:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1f8a92e34d1'
down_revision = '195a8571f735'
branch_labels = None
depends_on = None


def upgrade():
    # Expenses extensions
    op.add_column('expenses', sa.Column('is_recurring', sa.Boolean(), server_default=sa.text('false'), nullable=True))
    op.add_column('expenses', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('expenses', sa.Column('installments', sa.Integer(), server_default='1', nullable=True))

    # Budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('allocated_amount', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budgets_id'), 'budgets', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_budgets_id'), table_name='budgets')
    op.drop_table('budgets')
    op.drop_column('expenses', 'installments')
    op.drop_column('expenses', 'payment_method')
    op.drop_column('expenses', 'is_recurring')
