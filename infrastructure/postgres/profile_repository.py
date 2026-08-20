import os
try:
    import psycopg2
except Exception:
    psycopg2 = None
from typing import Optional, List, Dict


def _get_db_conn():
    if psycopg2 is None:
        raise ImportError("psycopg2 is required for PostgresProfileRepository")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


class PostgresProfileRepository:
    def get_profile(self, user_id: int) -> Optional[Dict]:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, surname, email, address, phone FROM profile WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            if row is None:
                cur.close()
                conn.close()
                return None

            cur.execute(
                """SELECT id, car_key, plate, is_default, added_at
                   FROM user_cars WHERE profile_id = %s
                   ORDER BY is_default DESC""",
                (user_id,),
            )
            cars = cur.fetchall()
            cur.close()
            conn.close()

            return {
                "id": str(row[0]),
                "name": row[1],
                "surname": row[2],
                "email": row[3],
                "address": row[4],
                "phone": row[5],
                "cars": [
                    {
                        "id": str(c[0]),
                        "car_key": c[1],
                        "plate": c[2],
                        "is_default": c[3],
                        "added_at": str(c[4]),
                    }
                    for c in cars
                ],
            }

        except Exception:
            if conn:
                conn.close()
            raise

    def update_profile(self, user_id: int, data: dict) -> Optional[Dict]:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                """UPDATE profile
                   SET name     = COALESCE(%s, name),
                       surname  = COALESCE(%s, surname),
                       address  = COALESCE(%s, address),
                       phone    = COALESCE(%s, phone),
                       home_lat = COALESCE(%s, home_lat),
                       home_lng = COALESCE(%s, home_lng)
                   WHERE id = %s
                   RETURNING id, name, surname, email, address, phone""",
                (
                    data.get("name"),
                    data.get("surname"),
                    data.get("address"),
                    data.get("phone"),
                    data.get("latitude"),
                    data.get("longitude"),
                    user_id,
                ),
            )
            row = cur.fetchone()
            if row is None:
                cur.close()
                conn.close()
                return None
            conn.commit()
            cur.close()
            conn.close()
            return {
                "id": str(row[0]),
                "name": row[1],
                "surname": row[2],
                "email": row[3],
                "address": row[4],
                "phone": row[5],
            }
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def add_car(self, user_id: int, car_key: str, plate: str) -> Dict:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM user_cars WHERE profile_id = %s", (user_id,))
            count = cur.fetchone()[0]
            is_default = count == 0

            cur.execute(
                """INSERT INTO user_cars (profile_id, car_key, plate, is_default)
                   VALUES (%s, %s, %s, %s)
                   RETURNING id, car_key, plate, is_default, added_at""",
                (user_id, car_key, plate, is_default),
            )
            row = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return {
                "id": str(row[0]),
                "car_key": row[1],
                "plate": row[2],
                "is_default": row[3],
                "added_at": str(row[4]),
            }
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def delete_car(self, user_id: int, car_id: int) -> bool:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT is_default FROM user_cars WHERE id = %s AND profile_id = %s",
                (car_id, user_id),
            )
            row = cur.fetchone()
            if row is None:
                cur.close()
                conn.close()
                return False

            was_default = row[0]
            cur.execute("DELETE FROM user_cars WHERE id = %s AND profile_id = %s", (car_id, user_id))

            if was_default:
                cur.execute(
                    """UPDATE user_cars SET is_default = true
                       WHERE id = (
                           SELECT id FROM user_cars
                           WHERE profile_id = %s
                           ORDER BY added_at ASC
                           LIMIT 1
                       )""",
                    (user_id,),
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

    def set_default_car(self, user_id: int, car_id: int) -> bool:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM user_cars WHERE id = %s AND profile_id = %s", (car_id, user_id))
            if cur.fetchone() is None:
                cur.close()
                conn.close()
                return False

            cur.execute("UPDATE user_cars SET is_default = false WHERE profile_id = %s", (user_id,))
            cur.execute("UPDATE user_cars SET is_default = true WHERE id = %s", (car_id,))

            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def get_charging_history(self, user_id: int) -> List[Dict]:
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                """SELECT id, station_key, price, energy_kwh, duration_min, connector_type, total_time
                   FROM charging_detail
                   WHERE profile_id = %s
                   ORDER BY total_time DESC""",
                (user_id,),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [
                {
                    "id": str(r[0]),
                    "station_key": r[1],
                    "price": r[2],
                    "energy_kwh": r[3],
                    "duration_min": r[4],
                    "connector_type": r[5],
                    "total_time": str(r[6]),
                }
                for r in rows
            ]
        except Exception:
            if conn:
                conn.close()
            raise
