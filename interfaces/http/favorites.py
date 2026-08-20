"""HTTP adapter for favorites endpoints using DDD services."""

from application.favorites_service import FavoritesService
from infrastructure.postgres.favorites_repository import PostgresFavoritesRepository

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


favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")

_repo = PostgresFavoritesRepository()
_service = FavoritesService(_repo)


@favorites_bp.route("/", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())
    try:
        rows = _service.list_favorites(user_id)
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorites_bp.route("/", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True)
    station_key = data.get("station_key")
    if not station_key:
        return jsonify({"error": "station_key gerekli"}), 400
    try:
        res = _service.add_favorite(user_id, station_key)
        return jsonify(res), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@favorites_bp.route("/<path:station_key>", methods=["DELETE"])
@jwt_required()
def remove_favorite(station_key):
    user_id = int(get_jwt_identity())
    try:
        ok = _service.remove_favorite(user_id, station_key)
        if ok:
            return jsonify({"success": True}), 200
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

__all__ = ["favorites_bp"]
 
