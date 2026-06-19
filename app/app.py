from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.favorites import favorites_bp
from routes.journey import journey_bp
from services.model import OpenRouterClient
from datetime import timedelta
import asyncio
import os

# NOTE model tek istekte 0.003$ harcadı :)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "degistir-bunu")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(favorites_bp)
app.register_blueprint(journey_bp)


# Launch a client
client = OpenRouterClient()
MCP_SCRIPT_PATH = "./data/loaders/station_server.py"


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {"status": "running", "message": "OpenRouter API is up and running."}
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    vehicle_info = data.get("vehicle", None)

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    print(f"Received message: {user_message}")

    # Send to model
    try:
        print(f"MCP script path: {MCP_SCRIPT_PATH}")
        response_text = asyncio.run(
            client.chat_with_mcp(
                user_message=user_message,
                mcp_script_path=MCP_SCRIPT_PATH,
                model="x-ai/grok-4.1-fast",
                vehicle_info=vehicle_info,
            )
        )
        print(f"Model response: {response_text}")
        return jsonify({"success": True, "response": response_text})

    except Exception as e:
        print(f"An error occurred in /chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting OpenRouter API server...")
    app.run(host="0.0.0.0", port=8000, debug=True)
