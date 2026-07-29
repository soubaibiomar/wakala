"""
apps/api/db/postgres.py
Client PostgreSQL pour les données opérationnelles Wakala.
Tables restructurées :
  - listings (id, prix, carburant, transmission, ...)  (ex-annonces/vehicles)
  - users (id, persona_dominant, n_interactions, ...)  (ex-utilisateurs)

Note sur l'historique du Chat :
  La gestion de l'historique du chat en temps réel (mémoire courte / session active)
  est gérée côté Redis (stockage à chaud). 
  Les tables PostgreSQL `chat_sessions` et `chat_messages` ne servent que d'archives
  à long-terme (stockage à froid) une fois la session clôturée.

Les imports psycopg2 sont différés pour permettre l'exécution des tests
avec des mocks sans dépendance installée.
"""
import os
import logging

logger = logging.getLogger("wakala.db.postgres")

# Connexion configurable via variables d'environnement
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "wakala")
PG_USER = os.getenv("PG_USER", "wakala")
PG_PASSWORD = os.getenv("PG_PASSWORD", "wakala")


class PostgresClient:
    def __init__(self, dsn: str | None = None):
        """
        Args:
            dsn: chaîne de connexion complète (optionnelle).
                 Si None, construit depuis les variables d'environnement.
        """
        self._dsn = dsn or f"host={PG_HOST} port={PG_PORT} dbname={PG_DB} user={PG_USER} password={PG_PASSWORD}"
        self._conn = None

    def _get_conn(self):
        if self._conn is None or self._conn.closed:
            import psycopg2
            self._conn = psycopg2.connect(self._dsn)
        return self._conn

    def get_user(self, user_id: str) -> dict:
        """
        Retourne les infos utilisateur depuis la table `users`.
        Colonnes attendues : id, persona_dominant, n_interactions.
        """
        import psycopg2.extras

        conn = self._get_conn()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, persona_dominant, n_interactions FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            if row is None:
                logger.warning(f"Utilisateur {user_id} non trouvé, retour cold-start par défaut.")
                return {"id": user_id, "persona_dominant": "Unknown", "n_interactions": 0}
            return dict(row)

    def get_cars_by_hard_filters(self, filters: dict) -> list[str]:
        """
        Applique les hard_filters en SQL strict sur la table `listings`.
        Retourne la liste des IDs d'annonces correspondantes.

        Filtres supportés :
          - budget_max (int) → prix <= budget_max
          - places_min (int) → ignoré provisoirement (ou réajouter 'seats' à listings)
          - carburant (str)  → carburant = carburant
          - boite (str)      → transmission = boite
        """
        conn = self._get_conn()
        conditions = []
        params = []

        if "budget_max" in filters:
            conditions.append("prix <= %s")
            params.append(filters["budget_max"])

        if "carburant" in filters:
            conditions.append("carburant = %s")
            params.append(filters["carburant"])

        if "boite" in filters:
            conditions.append("transmission = %s")
            params.append(filters["boite"])

        # Si places_min est requis, il faudra rajouter 'seats' dans la table listings
        # (actuellement omis dans la simplification du schéma)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        query = f"SELECT id FROM listings WHERE {where_clause}"

        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [str(row[0]) for row in rows]

    def get_car_details(self, car_id: str) -> dict | None:
        """Retourne les détails complets d'une annonce pour l'explicabilité."""
        import psycopg2.extras

        conn = self._get_conn()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM listings WHERE id = %s", (car_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()
