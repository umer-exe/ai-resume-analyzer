import unittest
from unittest.mock import patch

from app import app
from services.analyzer import (
    analyze_profile,
    extract_skills,
)


SAMPLE_PROFILE = (
    "I am a computer science student with skills in Python, Flask, HTML, CSS, "
    "SQL, GitHub, and basic AI concepts. I have built academic projects using "
    "web development and databases. I am interested in software development, "
    "AI, and data analysis roles."
)


class AnalyzerTests(unittest.TestCase):
    def test_response_schema_scores_and_repeatability(self):
        first_result = analyze_profile(SAMPLE_PROFILE)
        second_result = analyze_profile(SAMPLE_PROFILE)

        self.assertEqual(first_result, second_result)
        self.assertEqual(
            set(first_result),
            {
                "score",
                "status",
                "summary",
                "checks",
                "category_analysis",
                "skills",
                "recommendations",
                "next_steps",
                "ml_prediction",
            },
        )
        self.assertIsInstance(first_result["score"], int)
        self.assertGreaterEqual(first_result["score"], 0)
        self.assertLessEqual(first_result["score"], 100)
        self.assertEqual(len(first_result["category_analysis"]), 6)
        self.assertEqual(
            sum(first_result["checks"].values()),
            len(first_result["category_analysis"]),
        )
        self.assertEqual(len(first_result["next_steps"]), 5)
        self.assertEqual(
            set(first_result["ml_prediction"]),
            {
                "predicted_category",
                "display_category",
                "confidence",
                "source",
                "message",
                "top_predictions",
            },
        )

        for category in first_result["category_analysis"]:
            self.assertIsInstance(category["score"], int)
            self.assertGreaterEqual(category["score"], 0)
            self.assertLessEqual(category["score"], 100)

    def test_phrase_matching_aliases_and_false_positive_prevention(self):
        skills = extract_skills(
            "JavaScript painting flasking C++ MACHINE LEARNING "
            "artificial intelligence JavaScript"
        )

        self.assertEqual(skills["Programming"], ["JavaScript", "C++"])
        self.assertEqual(
            skills["AI and Data"],
            ["Artificial Intelligence", "Machine Learning"],
        )
        self.assertNotIn("Java", skills["Programming"])
        self.assertNotIn("Flask", skills["Web Development"])

    def test_richer_profile_scores_higher_than_sparse_profile(self):
        sparse_result = analyze_profile("Python")
        rich_result = analyze_profile(
            "Summary:\n"
            "Computer science bachelor student and Python developer.\n"
            "Skills:\n- Python\n- Flask\n- SQL\n- GitHub\n- REST APIs\n"
            "Projects:\n- Built and tested a Flask API serving 500 users.\n"
            "Experience:\n- Intern developer for 6 months and improved "
            "processing time by 25%."
        )

        self.assertGreater(rich_result["score"], sparse_result["score"])

    def test_action_plan_is_quality_focused_without_role_prediction(self):
        result = analyze_profile(SAMPLE_PROFILE)

        self.assertEqual(len(result["next_steps"]), 5)
        self.assertNotIn("top_role", result)
        self.assertNotIn("recommended_roles", result)
        self.assertTrue(
            any("job descriptions" in step for step in result["next_steps"])
        )


class ApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_http_statuses_and_response_shapes(self):
        root_response = self.client.get("/")
        self.assertEqual(root_response.status_code, 200)
        self.assertEqual(
            root_response.get_json(),
            {
                "success": True,
                "data": {
                    "message": "AI Resume Analyzer API is running",
                    "status": "success",
                },
                "error": None,
            },
        )

        empty_response = self.client.post(
            "/api/v1/analyze",
            data={"profile_text": "   "},
        )
        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(
            empty_response.get_json(),
            {
                "success": False,
                "data": None,
                "error": "Profile text is required",
            },
        )

        success_response = self.client.post(
            "/api/v1/analyze",
            data={"profile_text": SAMPLE_PROFILE},
        )
        self.assertEqual(success_response.status_code, 200)
        self.assertTrue(success_response.get_json()["success"])

        missing_response = self.client.get("/missing")
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(
            missing_response.get_json(),
            {
                "success": False,
                "data": None,
                "error": "Route not found",
            },
        )

    def test_analyzer_failure_returns_safe_500_response(self):
        with patch("app.run_analysis", side_effect=RuntimeError("private detail")):
            response = self.client.post(
                "/api/v1/analyze",
                data={"profile_text": SAMPLE_PROFILE},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {
                "success": False,
                "data": None,
                "error": "Unable to analyze profile",
            },
        )
        self.assertNotIn("private detail", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
