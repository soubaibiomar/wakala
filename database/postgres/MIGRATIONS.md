# Wakala — PostgreSQL Migration Strategy & Decision Record

## 1. Initial Deployment Lifecycle (`/docker-entrypoint-initdb.d`)

> [!IMPORTANT]
> `/docker-entrypoint-initdb.d` executes SQL scripts **ONLY ONCE** when PostgreSQL initializes a brand-new, empty data directory (`PGDATA`).
> Once the production volume (`prod_postgres_data`) has been created on the VPS, dropping a new `.sql` file into `database/postgres/migrations/` and restarting the container will **NOT** apply it automatically.

### Current Baseline (Migrations 001 to 023)
* Files: `database/postgres/migrations/001_create_users.sql` through `023_add_detailed_vehicle_specs.sql` (24 files in total).
* Execution: Auto-mounted in `docker-compose.prod.yml` at:
  `- ./database/postgres/migrations:/docker-entrypoint-initdb.d:ro`
* Seeding: Catalog data is populated once via:
  `docker compose -f docker-compose.prod.yml exec backend python scripts/seed_morocco_new_cars.py`

---

## 2. Production Procedure for Migration #25 Onward

For any post-launch schema changes on the live production VPS:

### Step 1: Create the Migration File
Create a new versioned SQL script in `database/postgres/migrations/`:
```bash
database/postgres/migrations/025_<description>.sql
```

### Step 2: Authoring Rules
All future migrations must follow these safety practices:
1. **Wrap in a single transaction:**
   ```sql
   BEGIN;
   -- Schema modifications here
   COMMIT;
   ```
2. **Use idempotent clauses:**
   * `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`
   * `CREATE INDEX IF NOT EXISTS ...`
   * `CREATE TABLE IF NOT EXISTS ...`
3. **Never drop columns or tables without prior deprecation.**

### Step 3: Apply to Live Production Container
Apply the migration manually against the running PostgreSQL container via `docker exec`:

```bash
# From the project root on the VPS:
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U wakala_user -d wakala_db -v ON_ERROR_STOP=1 \
  < database/postgres/migrations/025_<description>.sql
```

### Step 4: Verify Application
Check that the changes were applied correctly:
```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U wakala_user -d wakala_db -c "\d+ <target_table>"
```

---

## 3. Long-Term Architecture Decision

* **Current Stage (Launch Phase):**
  Sequential raw SQL scripts applied via `psql` / `docker exec`. This avoids ORM migration state desyncs during the initial launch.
* **Next Stage (Post-Launch Evolution):**
  Before introducing complex zero-downtime schema changes or multi-engineer branches:
  * Connect Alembic properly to `Base.metadata` and create a `schema_migrations` tracking table, OR
  * Implement a lightweight Python startup migration runner that scans `database/postgres/migrations/*.sql`, checks against an applied migrations table, and executes pending scripts in order.
