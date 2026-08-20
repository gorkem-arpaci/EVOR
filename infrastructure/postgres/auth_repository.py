import os
from typing import Optional, Dict

try:
    import psycopg2
except Exception:
    psycopg2 = None

try:
    import bcrypt
except Exception:
    bcrypt = None

try:
    import resend
except Exception:
    resend = None


def _get_db_conn():
    if psycopg2 is None:
        raise ImportError("psycopg2 is required for PostgresAuthRepository")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


class PostgresAuthRepository:
    def __init__(self):
        if resend is not None and os.getenv("RESEND_API_KEY"):
            resend.api_key = os.environ.get("RESEND_API_KEY")

    def register(self, user_data: Dict) -> Dict:
        if bcrypt is None:
            raise ImportError("bcrypt required for password hashing")
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            hashed = bcrypt.hashpw(user_data['password'].encode(), bcrypt.gensalt()).decode()
            cur.execute(
                """INSERT INTO profile (name, surname, email, phone, password, address, home_lat, home_lng)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (
                    user_data.get('name'),
                    user_data.get('surname'),
                    user_data['email'],
                    user_data.get('phone'),
                    hashed,
                    user_data.get('address'),
                    user_data.get('latitude'),
                    user_data.get('longitude'),
                ),
            )
            row = cur.fetchone()
            if row is None:
                conn.rollback()
                cur.close()
                conn.close()
                raise RuntimeError('user creation failed')
            user_id = row[0]
            if user_data.get('vehicle_brand') and user_data.get('vehicle_model'):
                car_key = f"{user_data.get('vehicle_brand')}_{user_data.get('vehicle_model')}'.lower().replace(' ', '_')"
                cur.execute(
                    "INSERT INTO user_cars (profile_id, car_key, plate, is_default) VALUES (%s, %s, %s, %s)",
                    (user_id, car_key, user_data.get('vehicle_plate'), True),
                )
            conn.commit()
            cur.close()
            conn.close()
            return {"user_id": user_id}
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def create_verification(self, email: str) -> Dict:
        # create a 6-digit code, insert to DB and send via resend if available
        import random
        from datetime import datetime, timedelta

        code = ''.join(random.choices('0123456789', k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=1)
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM email_verifications WHERE email = %s", (email,))
            cur.execute(
                "INSERT INTO email_verifications (email, code, expires_at) VALUES (%s, %s, %s)",
                (email, code, expires_at),
            )
            conn.commit()
            cur.close()
            conn.close()

            if resend is not None:
                params = {
                    'from': 'EVOR <onboarding@resend.dev>',
                    'to': [email],
                    'subject': 'Evor Doğrulama Kodu',
                    'html': f'<h1>{code}</h1>'
                }
                try:
                    resend.Emails.send(params)
                except Exception:
                    pass

            return {"message": "Doğrulama kodu gönderildi"}
        except Exception:
            if conn:
                conn.rollback()
                conn.close()
            raise

    def verify_code(self, email: str, code: str) -> bool:
        from datetime import datetime
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, expires_at, used FROM email_verifications WHERE email = %s AND code = %s ORDER BY created_at DESC LIMIT 1",
                (email, code),
            )
            row = cur.fetchone()
            if row is None:
                cur.close()
                conn.close()
                return False
            verification_id, expires_at, used = row[0], row[1], row[2]
            if used:
                cur.close()
                conn.close()
                return False
            if datetime.utcnow() > expires_at:
                cur.close()
                conn.close()
                return False
            cur.execute("UPDATE email_verifications SET used = TRUE WHERE id = %s", (verification_id,))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception:
            if conn:
                conn.close()
            raise

    def login(self, email: str, password: str) -> Optional[Dict]:
        if bcrypt is None:
            raise ImportError('bcrypt required for login')
        conn = None
        try:
            conn = _get_db_conn()
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM profile WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if not user or not bcrypt.checkpw(password.encode(), user[1].encode() if isinstance(user[1], str) else user[1]):
                return None
            return {"user_id": str(user[0])}
        except Exception:
            if conn:
                conn.close()
            raise
