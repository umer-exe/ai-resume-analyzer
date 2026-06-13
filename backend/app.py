import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from services.analyzer import analyze_profile as run_analysis
from services.resume_parser import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MESSAGE,
    ResumeFileTooLargeError,
    ResumeParseError,
    extract_resume_text,
)

app = Flask(__name__)
# Allow a small amount of multipart metadata beyond the actual file limit.
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES + (64 * 1024)
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
    resume_file = request.files.get("resume_file")
    has_resume_file = bool(resume_file and resume_file.filename)

    if profile_text and has_resume_file:
        return api_response(
            False,
            error="Provide either profile text or a resume file, not both",
            status_code=400,
        )

    if not profile_text and not has_resume_file:
        return api_response(
            False,
            error="Profile text or a resume file is required",
            status_code=400,
        )

    try:
        if has_resume_file:
            profile_text = extract_resume_text(resume_file)
        analysis_data = run_analysis(profile_text)
    except ResumeFileTooLargeError as error:
        return api_response(
            False,
            error=str(error),
            status_code=413,
        )
    except ResumeParseError as error:
        return api_response(
            False,
            error=str(error),
            status_code=400,
        )
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


@app.errorhandler(413)
def request_too_large(_error):
    return api_response(
        False,
        error=MAX_FILE_SIZE_MESSAGE,
        status_code=413,
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
    app.run(host="127.0.0.1", port=8000, debug=debug_mode)
