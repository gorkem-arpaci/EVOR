import resend
import os
import bcrypt
import psycopg2
import random
import string
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
resend.api_key = os.environ["RESEND_API_KEY"]


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    surname = data.get("surname")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    address = data.get("address")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    vehicle_brand = data.get("vehicle_brand")
    vehicle_model = data.get("vehicle_model")
    vehicle_plate = data.get("vehicle_plate")

    if not email or not password:
        return jsonify({"error": "Email ve şifre gerekli"}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = None

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO profile (name, surname, email, phone, password, address, home_lat, home_lng)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (name, surname, email, phone, hashed, address, latitude, longitude),
        )
        row = cur.fetchone()
        if row is None:
            return jsonify({"error": "Kullanıcı oluşturulamadı"}), 500
        user_id = row[0]

        if vehicle_brand and vehicle_model:
            car_key = f"{vehicle_brand}_{vehicle_model}".lower().replace(" ", "_")
            cur.execute(
                """INSERT INTO user_cars (profile_id, car_key, plate, is_default) VALUES (%s, %s, %s, %s)""",
                (user_id, car_key, vehicle_plate, True),
            )
        conn.commit()
        cur.close()
        conn.close()

    except psycopg2.errors.UniqueViolation:
        if conn is not None:
            conn.rollback()
            conn.close()
        return jsonify({"error": "Bu email zaten kayıtlı"}), 409
    except Exception as e:
        if conn is not None:
            conn.rollback()
            conn.close()
        print(f"🔴 Register error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

    token = create_access_token(identity=user_id)
    return jsonify({"token": token, "user_id": user_id}), 201


@auth_bp.route("/send-verification", methods=["POST"])
def send_verification():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email gerekli"}), 400

    code = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=1)

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        # Eski kodları sil
        cur.execute("DELETE FROM email_verifications WHERE email = %s", (email,))

        # Yeni kod ekle
        cur.execute(
            "INSERT INTO email_verifications (email, code, expires_at) VALUES (%s, %s, %s)",
            (email, code, expires_at),
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500

    # Email gönder
    try:
        params: resend.Emails.SendParams = {
            "from": "EVOR <onboarding@resend.dev>",
            "to": [email],
            "subject": "Evor Doğrulama Kodu",
            "html": f"""
                 <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto;">
                     <h2 style="color: #000;">EVOR Email Doğrulama</h2>
                     <p>Doğrulama kodunuz:</p>
                     <h1 style="letter-spacing: 8px; color: #000; font-size: 48px;">{code}</h1>
                     <p style="color: #666;">Bu kod 1 dakika geçerlidir.</p>
                 </div>
             """,
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"🔴 Email gönderme hatası: {type(e).__name__}: {e}")
        return jsonify({"error": "Doğrulama kodu gönderilirken hata oluştu"}), 500

    return jsonify({"message": "Doğrulama kodu gönderildi"}), 200


# MARK: - Kodu Doğrula
@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json(force=True)
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "Email ve kod gerekli"}), 400

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """SELECT id, expires_at, used FROM email_verifications
               WHERE email = %s AND code = %s
               ORDER BY created_at DESC LIMIT 1""",
            (email, code),
        )
        row = cur.fetchone()

        if row is None:
            cur.close()
            conn.close()
            return jsonify({"error": "Geçersiz kod"}), 400

        verification_id, expires_at, used = row[0], row[1], row[2]

        if used:
            cur.close()
            conn.close()
            return jsonify({"error": "Bu kod zaten kullanıldı"}), 400

        if datetime.utcnow() > expires_at:
            cur.close()
            conn.close()
            return jsonify({"error": "Kodun süresi doldu"}), 400

        # Kodu kullanıldı olarak işaretle
        cur.execute(
            "UPDATE email_verifications SET used = TRUE WHERE id = %s",
            (verification_id,),
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"verified": True}), 200

    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email ve şifre gerekli"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM profile WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not bcrypt.checkpw(password.encode(), user[1].encode()):
        return jsonify({"error": "Email veya şifre hatalı"}), 401

    token = create_access_token(identity=str(user[0]))
    return jsonify({"token": token, "user_id": str(user[0])}), 200
