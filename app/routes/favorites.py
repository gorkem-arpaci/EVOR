from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from urllib.parse import unquote
import psycopg2
import os

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@favorites_bp.route("/", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, station_key, added_at FROM favorite_stations WHERE profile_id = %s ORDER BY added_at DESC",
            (user_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(
            [
                {"id": str(r[0]), "station_key": r[1], "added_at": str(r[2])}
                for r in rows
            ]
        ), 200
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500


@favorites_bp.route("/", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    data = request.get_json(force=True)
    station_key = data.get("station_key")

    if not station_key:
        return jsonify({"error": "station_key gerekli"}), 400

    conn = None
    try:
        conn = get_db()
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
        return jsonify({"success": True}), 201
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500


@favorites_bp.route("/<path:station_key>", methods=["DELETE"])
@jwt_required()
def remove_favorite(station_key):
    station_key = unquote(station_key)
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM favorite_stations WHERE profile_id = %s AND station_key = %s",
            (user_id, station_key),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500
