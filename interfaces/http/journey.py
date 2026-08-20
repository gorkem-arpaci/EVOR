"""HTTP adapter for journey endpoints using DDD services."""

from application.journey_service import JourneyService
from infrastructure.postgres.journey_repository import PostgresJourneyRepository

# Optional Flask imports for safe static checks
try:
    from flask import Blueprint, jsonify, request
    from flask_jwt_extended import jwt_required, get_jwt_identity
    _HAS_FLASK = True
except Exception:
    _HAS_FLASK = False

    class Blueprint:
        def __init__(self, *a, **k):
            pass

        def route(self, *a, **k):
            def deco(f):
                return f

            return deco

    def jsonify(x):
        return x

    class _DummyRequest:
        def get_json(self, *a, **k):
            raise RuntimeError("Flask not installed")

    request = _DummyRequest()

    def jwt_required():
        def deco(f):
            return f

        return deco

    def get_jwt_identity():
        raise RuntimeError("Flask not installed")


journey_bp = Blueprint("journey", __name__, url_prefix="")

_repo = PostgresJourneyRepository()
_service = JourneyService(_repo)


@journey_bp.route("/journey", methods=["POST"])
@jwt_required()
def save_journey():
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Request body boş"}), 400
    try:
        res = _service.save_journey(user_id, data)
        return jsonify({"message": "Yolculuk kaydedildi", "journey_id": res.get("journey_id")}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@journey_bp.route("/journey", methods=["GET"])
@jwt_required()
def get_journeys():
    user_id = int(get_jwt_identity())
    try:
        rows = _service.list_journeys(user_id)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@journey_bp.route("/journey/<journey_id>", methods=["GET"])
@jwt_required()
def get_journey_detail(journey_id):
    user_id = int(get_jwt_identity())
    try:
        row = _service.get_journey_detail(user_id, int(journey_id))
        if row is None:
            return jsonify({"error": "Yolculuk bulunamadı"}), 404
        return jsonify(row), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

__all__ = ["journey_bp"]
 
