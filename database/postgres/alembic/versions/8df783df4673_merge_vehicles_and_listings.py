"""Merge vehicles and listings

Revision ID: 8df783df4673
Revises: 83a7b3142877
Create Date: 2026-07-29 18:20:42.862961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8df783df4673'
down_revision: Union[str, Sequence[str], None] = '83a7b3142877'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op
    import sqlalchemy as sa
    
    # Enums
    op.execute("CREATE TYPE sourceplateforme AS ENUM ('avito', 'moteur', 'wandaloo', 'global_occaz', 'otoclic', 'kifal_auto', 'spoticar')")
    op.execute("CREATE TYPE listingtype AS ENUM ('neuf', 'occasion')")
    op.execute("CREATE TYPE trustsignaltype AS ENUM ('anomalie_prix', 'dommage_photo', 'profil_vendeur_suspect', 'incoherence_titre_description')")

    # Sellers
    op.create_table(
        'sellers',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nom_affiche', sa.String(255), nullable=False),
        sa.Column('plateforme', sa.String(100), nullable=False),
        sa.Column('date_inscription_plateforme', sa.DateTime(timezone=True)),
        sa.Column('nb_annonces_actives', sa.Integer(), nullable=False, server_default='0')
    )

    # Rename old listings and vehicles to keep data
    # (In a real deployment, we'd copy data here and map foreign keys)
    op.execute("ALTER TABLE listings RENAME TO old_listings")
    op.execute("ALTER TABLE vehicles RENAME TO old_vehicles")

    # Create new listings table
    op.create_table(
        'listings',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('source_plateforme', sa.Enum('avito', 'moteur', 'wandaloo', 'global_occaz', 'otoclic', 'kifal_auto', 'spoticar', name='sourceplateforme'), nullable=False),
        sa.Column('type_annonce', sa.Enum('neuf', 'occasion', name='listingtype'), nullable=False),
        sa.Column('certifie', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('marque', sa.String(100), nullable=False),
        sa.Column('modele', sa.String(100), nullable=False),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('prix', sa.Numeric(12, 2), nullable=False),
        sa.Column('kilometrage', sa.Integer()),
        sa.Column('carburant', sa.String(50)),
        sa.Column('transmission', sa.String(50)),
        sa.Column('categorie', sa.String(50)),
        sa.Column('tags', sa.ARRAY(sa.String())),
        sa.Column('vendeur_id', sa.UUID(as_uuid=True), sa.ForeignKey('sellers.id')),
        sa.Column('url_source', sa.String(500)),
        sa.Column('date_publication', sa.DateTime(timezone=True)),
        sa.Column('score_confiance', sa.Numeric(5, 4)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    
    # Trust Signals
    op.create_table(
        'trust_signals',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('listing_id', sa.UUID(as_uuid=True), sa.ForeignKey('listings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type_signal', sa.Enum('anomalie_prix', 'dommage_photo', 'profil_vendeur_suspect', 'incoherence_titre_description', name='trustsignaltype'), nullable=False),
        sa.Column('severite', sa.Numeric(5, 4), nullable=False),
        sa.Column('detail', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

def downgrade() -> None:
    from alembic import op
    op.drop_table('trust_signals')
    op.drop_table('listings')
    op.execute("ALTER TABLE old_vehicles RENAME TO vehicles")
    op.execute("ALTER TABLE old_listings RENAME TO listings")
    op.drop_table('sellers')
    op.execute("DROP TYPE IF EXISTS trustsignaltype;")
    op.execute("DROP TYPE IF EXISTS listingtype;")
    op.execute("DROP TYPE IF EXISTS sourceplateforme;")
