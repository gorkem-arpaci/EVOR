from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psycopg2
import os
from datetime import datetime

journey_bp = Blueprint("journey", __name__, url_prefix="")


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# ---------------------------------------------------------------------------
# POST /journey/journey  —  Yolculuk kaydet
# ---------------------------------------------------------------------------
@journey_bp.route("/journey", methods=["POST"])
@jwt_required()
def save_journey():
    user_id = get_jwt_identity()
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Request body boş"}), 400
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO journey (
                user_id, vehicle_id,
                start_location, end_location,
                start_time, season, weather_conditions,
                total_distance_km, total_driving_time_min,
                total_charging_time_min, total_trip_time_min,
                total_energy_needed_kwh,
                starting_soc_percent, ending_soc_percent,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id""",
            (
                user_id,
                data.get("vehicle_id"),
                data.get("start_location", ""),
                data.get("end_location", ""),
                data.get("start_time"),
                data.get("season"),
                data.get("weather_conditions"),
                data.get("total_distance_km"),
                data.get("total_driving_time_min"),
                data.get("total_charging_time_min"),
                data.get("total_trip_time_min"),
                data.get("total_energy_needed_kwh"),
                data.get("starting_soc_percent"),
                data.get("ending_soc_percent"),
                datetime.utcnow(),
            ),
        )
        journey_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {"message": "Yolculuk kaydedildi", "journey_id": str(journey_id)}
        ), 201
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"Save journey error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# GET /journey/journey  —  Kullanıcının geçmiş yolculukları
# ---------------------------------------------------------------------------
@journey_bp.route("/journey", methods=["GET"])
@jwt_required()
def get_journeys():
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """SELECT j.id, j.start_location, j.end_location, j.start_time,
              j.total_distance_km, j.total_trip_time_min,
              j.starting_soc_percent, j.ending_soc_percent,
              j.created_at,
              COUNT(js.id) AS stop_count
       FROM journey j
       LEFT JOIN journey_stop js ON js.journey_id = j.id
       WHERE j.user_id = %s
       GROUP BY j.id
       ORDER BY j.created_at DESC
       LIMIT 20""",
            (user_id,),
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(
            [
                {
                    "id": str(r[0]),
                    "start_location": r[1],
                    "end_location": r[2],
                    "start_time": str(r[3]) if r[3] else None,
                    "total_distance_km": r[4],
                    "total_trip_time_min": r[5],
                    "starting_soc_percent": r[6],
                    "ending_soc_percent": r[7],
                    "created_at": r[8].isoformat() if r[8] else None,
                    "stop_count": r[9],
                }
                for r in rows
            ]
        ), 200

    except Exception as e:
        if conn:
            conn.close()
        print(f"Get journeys error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


@journey_bp.route("/journey/<journey_id>", methods=["GET"])
@jwt_required()
def get_journey_detail(journey_id):
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        # Önce journey tablosunu sorgula
        cur.execute(
            """SELECT id, start_location, end_location, start_time,
                      total_distance_km, total_driving_time_min,
                      total_charging_time_min, total_trip_time_min,
                      total_energy_needed_kwh, starting_soc_percent,
                      ending_soc_percent, season, weather_conditions, created_at
               FROM journey
               WHERE id = %s AND user_id = %s""",
            (journey_id, user_id),
        )
        row = cur.fetchone()

        if row is None:
            cur.close()
            conn.close()
            return jsonify({"error": "Yolculuk bulunamadı"}), 404

        # Sonra stop'ları sorgula
        cur.execute(
            """SELECT stop_number, station_name, provider,
                      connector_type, estimated_power_kw,
                      energy_added_kwh, charge_time_min,
                      arrival_soc_percent, charge_to_percent,
                      arrival_time, departure_time, reason
               FROM journey_stop
               WHERE journey_id = %s
               ORDER BY stop_number""",
            (journey_id,),
        )
        stops = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(
            {
                "id": str(row[0]),
                "start_location": row[1],
                "end_location": row[2],
                "start_time": str(row[3]) if row[3] else None,
                "total_distance_km": row[4],
                "total_driving_time_min": row[5],
                "total_charging_time_min": row[6],
                "total_trip_time_min": row[7],
                "total_energy_needed_kwh": float(row[8]) if row[8] else None,
                "starting_soc_percent": row[9],
                "ending_soc_percent": row[10],
                "season": row[11],
                "weather_conditions": row[12],
                "stops": [
                    {
                        "stop_number": s[0],
                        "station_name": s[1],
                        "provider": s[2],
                        "connector_type": s[3],
                        "estimated_power_kw": float(s[4]) if s[4] else None,
                        "energy_added_kwh": float(s[5]) if s[5] else None,
                        "charge_time_min": s[6],
                        "arrival_soc_percent": s[7],
                        "charge_to_percent": s[8],
                        "arrival_time": str(s[9]) if s[9] else None,
                        "departure_time": str(s[10]) if s[10] else None,
                        "reason": s[11],
                    }
                    for s in stops
                ],
            }
        ), 200

    except Exception as e:
        if conn:
            conn.close()
        print(f"Get journey detail error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500
