from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Temporary Phase 5.5 data. Phase 6 will replace this with analyzer service output.
DUMMY_ANALYSIS_DATA = {
    "score": 75,
    "status": "Moderate",
    "summary": (
        "Your profile has a good technical foundation but needs "
        "stronger project details and role-specific keywords."
    ),
    "top_role": "Python Developer Intern",
    "checks": {
        "passed": 3,
        "warnings": 2,
        "issues": 1,
    },
    "category_analysis": [
        {
            "category": "Skills",
            "score": 80,
            "status": "Good",
            "feedback": "Relevant technical skills are present.",
        },
        {
            "category": "Projects",
            "score": 55,
            "status": "Needs Work",
            "feedback": (
                "Project descriptions need more detail and measurable outcomes."
            ),
        },
        {
            "category": "Experience",
            "score": 78,
            "status": "Good",
            "feedback": (
                "Experience shows a useful foundation for entry-level "
                "technical roles."
            ),
        },
        {
            "category": "Education",
            "score": 72,
            "status": "Good",
            "feedback": (
                "Education supports the target roles and is presented clearly."
            ),
        },
        {
            "category": "ATS Keywords",
            "score": 65,
            "status": "Warning",
            "feedback": (
                "Add more role-specific keywords used in relevant job "
                "descriptions."
            ),
        },
        {
            "category": "Formatting",
            "score": 68,
            "status": "Warning",
            "feedback": (
                "Improve consistency across headings, spacing, and bullet points."
            ),
        },
    ],
    "skills": {
        "Programming": ["Python", "SQL"],
        "Web Development": ["HTML", "CSS", "Flask"],
        "AI and Data": ["Basic AI Concepts"],
        "Cybersecurity and Networking": [],
        "Cloud and Tools": ["GitHub"],
    },
    "recommended_roles": [
        {
            "role": "Python Developer Intern",
            "match_percentage": 75,
            "matched_skills": ["Python", "Flask"],
            "missing_skills": ["Django", "APIs"],
        },
    ],
    "recommendations": {
        "high_priority": [
            "Add measurable achievements to experience and project descriptions.",
            "Add stronger role-specific keywords.",
        ],
        "medium_priority": [
            "Add a GitHub or portfolio link.",
            "Improve project descriptions with tools and outcomes.",
        ],
        "low_priority": [
            "Improve formatting consistency.",
            "Add a short professional summary.",
        ],
    },
    "next_steps": [
        "Improve resume structure with clear sections.",
        "Add 2 to 3 strong projects.",
        "Learn missing technical skills.",
        "Upload projects to GitHub.",
        "Apply for internships or entry-level roles.",
    ],
}


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

    return api_response(True, DUMMY_ANALYSIS_DATA)


@app.errorhandler(404)
def route_not_found(_error):
    return api_response(
        False,
        error="Route not found",
        status_code=404,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
