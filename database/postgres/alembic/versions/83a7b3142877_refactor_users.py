"""Refactor users

Revision ID: 83a7b3142877
Revises: 63c213876e75
Create Date: 2026-07-29 18:20:21.666408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83a7b3142877'
down_revision: Union[str, Sequence[str], None] = '63c213876e75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op
    import sqlalchemy as sa
    
    # Add city, persona_dominant and n_interactions to users table
    op.add_column('users', sa.Column('city', sa.String(length=150), nullable=True))
    op.add_column('users', sa.Column('persona_dominant', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('n_interactions', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    from alembic import op
    
    op.drop_column('users', 'n_interactions')
    op.drop_column('users', 'persona_dominant')
    op.drop_column('users', 'city')
