"""HTTP adapter for profile endpoints implemented using DDD application service.

This module defines `profile_bp` endpoints that delegate to the
`ProfileService` in `application.profile_service` and use the
`PostgresProfileRepository` as the infrastructure adapter.
"""

from application.profile_service import ProfileService
from infrastructure.postgres.profile_repository import PostgresProfileRepository
from shared import get_station_info

# Make Flask imports optional for static import checks
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


profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

# Instantiate repository and service (simple composition for now)
_repo = PostgresProfileRepository()
_service = ProfileService(_repo)


@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
	user_id = int(get_jwt_identity())
	try:
		result = _service.get_profile(user_id)
		if result is None:
			return jsonify({"msg": "Profile not found"}), 404
		return jsonify(result), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@profile_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_profile():
	user_id = int(get_jwt_identity())
	data = request.get_json()
	if not data:
		return jsonify({"error": "Geçersiz JSON"}), 400
	try:
		updated = _service.update_profile(user_id, data)
		if updated is None:
			return jsonify({"msg": "Profile not found"}), 404
		return jsonify(updated), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@profile_bp.route("/cars", methods=["POST"])
@jwt_required()
def add_car():
	user_id = int(get_jwt_identity())
	data = request.get_json()
	car_key = data.get("car_key")
	plate = data.get("plate")
	if not car_key:
		return jsonify({"error": "car_key gerekli"}), 400
	try:
		row = _service.add_car(user_id, car_key, plate)
		return jsonify(row), 201
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@profile_bp.route("/cars/<car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
	user_id = int(get_jwt_identity())
	try:
		ok = _service.delete_car(user_id, int(car_id))
		if not ok:
			return jsonify({"error": "Araç bulunamadı"}), 404
		return jsonify({"success": True}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@profile_bp.route("/cars/<car_id>/default", methods=["PATCH"])
@jwt_required()
def set_default_car(car_id):
	user_id = int(get_jwt_identity())
	try:
		ok = _service.set_default_car(user_id, int(car_id))
		if not ok:
			return jsonify({"error": "Araç bulunamadı"}), 404
		return jsonify({"success": True}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@profile_bp.route("/charging-history", methods=["GET"])
@jwt_required()
def get_charging_history():
	user_id = int(get_jwt_identity())
	try:
		rows = _service.get_charging_history(user_id)
		# Enrich with station info where possible
		enriched = [
			{**r, **get_station_info(r.get("station_key"))} for r in rows
		]
		return jsonify(enriched), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

__all__ = ["profile_bp"]

