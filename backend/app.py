from flask import Flask, jsonify, request
from flask_cors import CORS

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

    return api_response(
        True,
        {
            "ats_score": 75,
            "skills": {
                "Programming": ["Python", "SQL"],
                "Web Development": ["HTML", "CSS", "Flask"],
                "AI and Data": ["Basic AI Concepts"],
                "Cybersecurity and Networking": [],
                "Cloud and Tools": ["GitHub"],
            },
            "strengths": [
                "Good technical foundation",
                "Profile includes programming and web development skills",
            ],
            "weaknesses": [
                "Resume needs more measurable achievements",
                "More project details should be added",
            ],
            "recommended_roles": [
                {
                    "role": "Python Developer Intern",
                    "match_percentage": 75,
                    "matched_skills": ["Python", "Flask"],
                    "missing_skills": ["Django", "APIs"],
                },
                {
                    "role": "Junior Web Developer",
                    "match_percentage": 70,
                    "matched_skills": ["HTML", "CSS"],
                    "missing_skills": ["JavaScript", "React"],
                },
                {
                    "role": "Data Analyst Intern",
                    "match_percentage": 55,
                    "matched_skills": ["SQL"],
                    "missing_skills": [
                        "Excel",
                        "Pandas",
                        "Data Visualization",
                    ],
                },
            ],
            "career_roadmap": [
                "Improve resume structure with clear sections",
                "Add 2 to 3 strong projects",
                "Learn missing technical skills",
                "Upload projects to GitHub",
                "Apply for internships or entry level roles",
            ],
        },
    )


@app.errorhandler(404)
def route_not_found(_error):
    return api_response(
        False,
        error="Route not found",
        status_code=404,
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
