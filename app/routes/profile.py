from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import os

from utils.station_lookup import get_station_info  # ← tek ekleme

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, name, surname, email, address, phone FROM profile WHERE id = %s",
            (user_id,),
        )
        row = cur.fetchone()

        if row is None:
            cur.close()
            conn.close()
            return jsonify({"msg": "Profile not found"}), 404

        cur.execute(
            """SELECT id, car_key, plate, is_default, added_at
               FROM user_cars WHERE profile_id = %s
               ORDER BY is_default DESC""",
            (user_id,),
        )
        cars = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(
            {
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
        ), 200

    except Exception as e:
        if conn is not None:
            conn.close()
        print(f"Get profile error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Geçersiz JSON"}), 400

    name = data.get("name")
    surname = data.get("surname")
    address = data.get("address")
    phone = data.get("phone")
    lat = data.get("latitude")
    lon = data.get("longitude")

    conn = None
    try:
        conn = get_db()
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
            (name, surname, address, phone, lat, lon, user_id),
        )

        row = cur.fetchone()

        if row is None:
            cur.close()
            conn.close()
            return jsonify({"msg": "Profile not found"}), 404

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(
            {
                "id": str(row[0]),
                "name": row[1],
                "surname": row[2],
                "email": row[3],
                "address": row[4],
                "phone": row[5],
            }
        ), 200

    except Exception as e:
        if conn is not None:
            conn.rollback()
            conn.close()
        import traceback

        traceback.print_exc()
        print(f"Update profile error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


@profile_bp.route("/cars", methods=["POST"])
@jwt_required()
def add_car():
    user_id = get_jwt_identity()
    data = request.get_json()

    car_key = data.get("car_key")
    plate = data.get("plate")

    if not car_key:
        return jsonify({"error": "car_key gerekli"}), 400

    conn = None
    try:
        conn = get_db()
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

        return jsonify(
            {
                "id": str(row[0]),
                "car_key": row[1],
                "plate": row[2],
                "is_default": row[3],
                "added_at": str(row[4]),
            }
        ), 201

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Add car error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


# MARK: - Araç Sil
@profile_bp.route("/cars/<car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT is_default FROM user_cars WHERE id = %s AND profile_id = %s",
            (car_id, user_id),
        )
        row = cur.fetchone()

        if row is None:
            cur.close()
            conn.close()
            return jsonify({"error": "Araç bulunamadı"}), 404

        was_default = row[0]

        cur.execute(
            "DELETE FROM user_cars WHERE id = %s AND profile_id = %s", (car_id, user_id)
        )

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
        return jsonify({"success": True}), 200

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Delete car error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


# MARK: - Varsayılan Araç Değiştir
@profile_bp.route("/cars/<car_id>/default", methods=["PATCH"])
@jwt_required()
def set_default_car(car_id):
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM user_cars WHERE id = %s AND profile_id = %s",
            (car_id, user_id),
        )
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return jsonify({"error": "Araç bulunamadı"}), 404

        cur.execute(
            "UPDATE user_cars SET is_default = false WHERE profile_id = %s", (user_id,)
        )
        cur.execute("UPDATE user_cars SET is_default = true WHERE id = %s", (car_id,))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True}), 200

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Set default car error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


# MARK: - Geçmiş şarj dolumların listesi
@profile_bp.route("/charging-history", methods=["GET"])
@jwt_required()
def get_charging_history():
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
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

        return jsonify(
            [
                {
                    "id": str(r[0]),
                    "station_key": r[1],
                    **get_station_info(r[1]),  # station_name + address
                    "price": r[2],
                    "energy_kwh": r[3],
                    "duration_min": r[4],
                    "connector_type": r[5],
                    "total_time": str(r[6]),
                }
                for r in rows
            ]
        ), 200

    except Exception as e:
        if conn:
            conn.close()
        print(f"Charging history error: {e}")
        return jsonify({"error": str(e)}), 500
