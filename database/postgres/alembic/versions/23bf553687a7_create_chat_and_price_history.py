"""Create chat and price history

Revision ID: 23bf553687a7
Revises: 8df783df4673
Create Date: 2026-07-29 18:21:24.730258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23bf553687a7'
down_revision: Union[str, Sequence[str], None] = '8df783df4673'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op
    import sqlalchemy as sa
    
    # Chat Role Enum
    op.execute("CREATE TYPE chatrole AS ENUM ('user', 'assistant')")

    # Chat Sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('listing_id', sa.UUID(as_uuid=True), sa.ForeignKey('listings.id', ondelete='SET NULL')),
        sa.Column('langue_detectee', sa.String(10)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('closed_at', sa.DateTime(timezone=True))
    )

    # Chat Messages
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('session_id', sa.UUID(as_uuid=True), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='chatrole'), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Price History
    op.create_table(
        'price_history',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('marque', sa.String(100), nullable=False),
        sa.Column('modele', sa.String(100), nullable=False),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('prix_moyen_marche', sa.Numeric(12, 2), nullable=False),
        sa.Column('date_releve', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_donnee', sa.String(100), nullable=False)
    )

def downgrade() -> None:
    from alembic import op
    
    op.drop_table('price_history')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.execute("DROP TYPE IF EXISTS chatrole;")
