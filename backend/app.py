import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from services.analyzer import analyze_profile as run_analysis

app = Flask(__name__)
CORS(app)


def api_response(success, data=None, error=None, status_code=200):
    return (
        jsonify(
            {
                "success": success,
                "data": data,
                "error": error,
            }
        ),
        status_code,
    )


@app.get("/")
def index():
    return api_response(
        True,
        {
            "message": "AI Resume Analyzer API is running",
            "status": "success",
        },
        status_code=200,
    )


@app.post("/api/v1/analyze")
def analyze_profile():
    profile_text = request.form.get("profile_text", "").strip()

    if not profile_text:
        return api_response(
            False,
            error="Profile text is required",
            status_code=400,
        )

    try:
        analysis_data = run_analysis(profile_text)
    except Exception:
        app.logger.exception("Profile analysis failed")
        return api_response(
            False,
            error="Unable to analyze profile",
            status_code=500,
        )

    return api_response(True, analysis_data, status_code=200)


@app.errorhandler(404)
def route_not_found(_error):
    return api_response(
        False,
        error="Route not found",
        status_code=404,
    )


@app.errorhandler(500)
def internal_server_error(_error):
    return api_response(
        False,
        error="Internal server error",
        status_code=500,
    )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
