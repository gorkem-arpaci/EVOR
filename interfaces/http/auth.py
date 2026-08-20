"""HTTP adapter for auth endpoints implemented using DDD application service.

Delegates registration, verification and login to `AuthService`.
"""

from datetime import datetime
from application.auth_service import AuthService
from infrastructure.postgres.auth_repository import PostgresAuthRepository

# Try to import Flask pieces; if not available (import-time checks), provide
# lightweight stubs so the module remains importable in environments without
# Flask installed. Endpoints will raise if actually executed without Flask.
try:
	from flask import Blueprint, jsonify, request
	from flask_jwt_extended import create_access_token
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

	def create_access_token(identity):
		raise RuntimeError("flask_jwt_extended not installed")


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_repo = PostgresAuthRepository()
_service = AuthService(_repo)


@auth_bp.route("/register", methods=["POST"])
def register():
	data = request.get_json()
	if not data or not data.get('email') or not data.get('password'):
		return jsonify({"error": "Email ve şifre gerekli"}), 400
	try:
		res = _service.register_user(data)
		token = create_access_token(identity=str(res['user_id']))
		return jsonify({"token": token, "user_id": res['user_id']}), 201
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@auth_bp.route("/send-verification", methods=["POST"])
def send_verification():
	data = request.get_json()
	email = data.get('email') if data else None
	if not email:
		return jsonify({"error": "Email gerekli"}), 400
	try:
		res = _service.send_verification(email)
		return jsonify(res), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
	data = request.get_json(force=True)
	email = data.get('email')
	code = data.get('code')
	if not email or not code:
		return jsonify({"error": "Email ve kod gerekli"}), 400
	try:
		ok = _service.verify_email(email, code)
		if not ok:
			return jsonify({"error": "Doğrulama başarısız"}), 400
		return jsonify({"verified": True}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
	data = request.get_json()
	email = data.get('email') if data else None
	password = data.get('password') if data else None
	if not email or not password:
		return jsonify({"error": "Email ve şifre gerekli"}), 400
	try:
		user = _service.login_user(email, password)
		if not user:
			return jsonify({"error": "Email veya şifre hatalı"}), 401
		token = create_access_token(identity=str(user['user_id']))
		return jsonify({"token": token, "user_id": user['user_id']}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

__all__ = ["auth_bp"]

