"""
Presentation layer: Flask app, routes, API key auth, request parsing.
"""
import hmac
from functools import wraps

from flask import Flask, jsonify, request

import config
from business import analyze_tick
from validators import validate_tick_payload

app = Flask(__name__)


def failure(message, status):
    return jsonify({"result": "failure", "message": message}), status


def require_api_key(func):
    """Reject requests whose 'apikey' header is missing or wrong."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        provided = request.headers.get("apikey", "")
        if not config.API_KEY or not hmac.compare_digest(provided, config.API_KEY):
            return failure("Unauthorized", 401)
        return func(*args, **kwargs)
    return wrapper


@app.route("/healthcheck", methods=["GET"])
@require_api_key
def healthcheck():
    try:
        return jsonify({"result": "success", "message": "Ready to Trade"}), 200
    except Exception as e:
        return jsonify({"result": "failure", "message": str(e)}), 200


@app.route("/tick", methods=["POST"])
@require_api_key
def tick():
    payload = request.get_json(silent=True)
    if payload is None:
        return failure("Invalid payload: body must be valid JSON", 400)

    try:
        validate_tick_payload(payload)
    except ValueError as e:
        return failure(f"Invalid payload: {e}", 400)

    try:
        return jsonify(analyze_tick(payload)), 200
    except Exception as e:
        return failure(f"Processing error: {e}", 500)


# Keep every response JSON, even for unknown routes and server errors
@app.errorhandler(404)
def not_found(_):
    return failure("Not found", 404)


@app.errorhandler(405)
def method_not_allowed(_):
    return failure("Method not allowed", 405)


@app.errorhandler(500)
def server_error(_):
    return failure("Internal server error", 500)


if __name__ == "__main__":
    if not config.API_KEY:
        print("WARNING: API_KEY is not set in .env — all requests will be rejected.")
    app.run(host=config.HOST, port=config.PORT, debug=False)
