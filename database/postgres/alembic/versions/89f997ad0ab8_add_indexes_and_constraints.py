"""Add indexes and constraints

Revision ID: 89f997ad0ab8
Revises: 23bf553687a7
Create Date: 2026-07-29 18:21:41.596583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89f997ad0ab8'
down_revision: Union[str, Sequence[str], None] = '23bf553687a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op
    
    # Indexes
    op.create_index('idx_listings_source_type', 'listings', ['source_plateforme', 'type_annonce'])
    op.create_index('idx_listings_marque_modele_annee', 'listings', ['marque', 'modele', 'annee'])
    op.create_index('idx_trust_signals_listing_id', 'trust_signals', ['listing_id'])
    op.create_index('idx_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])

    # Check constraint
    op.create_check_constraint('ck_trust_signals_severite', 'trust_signals', 'severite >= 0 AND severite <= 1')

def downgrade() -> None:
    from alembic import op
    
    op.drop_constraint('ck_trust_signals_severite', 'trust_signals', type_='check')
    op.drop_index('idx_chat_messages_session_created', table_name='chat_messages')
    op.drop_index('idx_trust_signals_listing_id', table_name='trust_signals')
    op.drop_index('idx_listings_marque_modele_annee', table_name='listings')
    op.drop_index('idx_listings_source_type', table_name='listings')
