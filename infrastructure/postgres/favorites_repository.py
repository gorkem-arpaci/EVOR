import os
try:
    import psycopg2
except Exception:
    psycopg2 = None

from typing import List, Dict


def _get_db_conn():
    if psycopg2 is None:
        raise ImportError("psycopg2 is required for PostgresFavoritesRepository")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


class PostgresFavoritesRepository:
    def list_favorites(self, user_id: int) -> List[Dict]:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, station_key, added_at FROM favorite_stations WHERE profile_id = %s ORDER BY added_at DESC",
                (user_id,),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [
                {"id": str(r[0]), "station_key": r[1], "added_at": str(r[2])}
                for r in rows
            ]
        except Exception:
            if conn:
                conn.close()
            raise

    def add_favorite(self, user_id: int, station_key: str) -> Dict:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO favorite_stations (profile_id, station_key)
                   VALUES (%s, %s)
                   ON CONFLICT (profile_id, station_key) DO NOTHING
                   RETURNING id""",
                (user_id, station_key),
            )
            conn.commit()
            cur.close()
            conn.close()
            return {"success": True}
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def remove_favorite(self, user_id: int, station_key: str) -> bool:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM favorite_stations WHERE profile_id = %s AND station_key = %s",
                (user_id, station_key),
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise
