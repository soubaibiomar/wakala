"""Baseline current schema

Revision ID: 63c213876e75
Revises: 
Create Date: 2026-07-29 18:19:59.930854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63c213876e75'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import os
    from alembic import op
    
    # Path to the old SQL migrations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    migrations_dir = os.path.join(base_dir, "..", "..", "migrations")
    
    sql_files = [
        "001_create_users.sql",
        "002_create_vehicles.sql",
        "003_create_listings.sql",
        "004_create_reviews.sql",
        "005_create_interactions.sql",
        "006_add_is_pro_to_users.sql",
        "007_create_scraper_health.sql",
        "007_create_transactions.sql",
        "008_auth_updates.sql",
        "009_require_phone.sql",
        "010_vehicle_soft_delete.sql",
        "011_add_full_name_to_users.sql",
        "012_add_missing_user_columns.sql",
        "013_maintenance_module.sql",
        "014_extend_source_list.sql"
    ]
    
    for f in sql_files:
        path = os.path.join(migrations_dir, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                sql = file.read()
                # Execute the raw SQL
                op.execute(sql)


def downgrade() -> None:
    from alembic import op
    # For a baseline, the downgrade is dropping everything.
    op.execute("DROP SCHEMA public CASCADE;")
    op.execute("CREATE SCHEMA public;")
