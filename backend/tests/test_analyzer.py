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

FIXED_ML_PREDICTION = {
    "predicted_category": None,
    "display_category": None,
    "confidence": 0,
    "source": "ml_classifier",
    "message": "ML model not trained yet",
    "top_predictions": [],
}


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        prediction_patcher = patch(
            "services.analyzer.predict_category",
            return_value=FIXED_ML_PREDICTION,
        )
        prediction_patcher.start()
        self.addCleanup(prediction_patcher.stop)

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
                "action_plan",
                "ml_prediction",
            },
        )
        self.assertIsInstance(first_result["score"], int)
        self.assertGreaterEqual(first_result["score"], 0)
        self.assertLessEqual(first_result["score"], 100)
        self.assertEqual(len(first_result["category_analysis"]), 6)
        self.assertEqual(
            [
                category["category"]
                for category in first_result["category_analysis"]
            ],
            [
                "Skills",
                "Projects",
                "Experience",
                "Education",
                "ATS Keywords",
                "Formatting",
            ],
        )
        self.assertEqual(
            sum(first_result["checks"].values()),
            len(first_result["category_analysis"]),
        )
        self.assertGreater(len(first_result["action_plan"]), 0)
        self.assertLessEqual(len(first_result["action_plan"]), 3)
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
            self.assertEqual(
                set(category),
                {"category", "score", "status", "feedback", "action"},
            )
            self.assertIsInstance(category["score"], int)
            self.assertGreaterEqual(category["score"], 0)
            self.assertLessEqual(category["score"], 100)
            self.assertTrue(category["action"])

    def test_phrase_matching_aliases_and_false_positive_prevention(self):
        skills = extract_skills(
            "JavaScript painting flasking C++ MACHINE LEARNING "
            "artificial intelligence JavaScript python PYTHON"
        )

        self.assertEqual(
            skills,
            [
                "Python",
                "JavaScript",
                "C++",
                "Artificial Intelligence",
                "Machine Learning",
            ],
        )
        self.assertNotIn("Java", skills)
        self.assertNotIn("Flask", skills)

    def test_skills_are_a_flat_ordered_unique_list(self):
        result = analyze_profile("GitHub Git SQL MySQL Python python Flask")

        self.assertEqual(
            result["skills"],
            ["Python", "SQL", "Flask", "GitHub", "Git"],
        )
        self.assertEqual(len(result["skills"]), len(set(result["skills"])))

    def test_no_detected_skills_returns_empty_list(self):
        result = analyze_profile("Organized student seeking an opportunity.")

        self.assertEqual(result["skills"], [])

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
        self.assertEqual(len(rich_result["action_plan"]), 1)
        self.assertEqual(rich_result["action_plan"][0]["priority"], "Low")

    def test_action_plan_is_quality_focused_without_role_prediction(self):
        result = analyze_profile(SAMPLE_PROFILE)

        self.assertGreater(len(result["action_plan"]), 0)
        self.assertLessEqual(len(result["action_plan"]), 3)
        self.assertEqual(
            len({item["category"] for item in result["action_plan"]}),
            len(result["action_plan"]),
        )
        for item in result["action_plan"]:
            self.assertEqual(set(item), {"category", "priority", "action"})
            self.assertIn(item["priority"], {"High", "Medium", "Low"})
            self.assertTrue(item["action"])
            category_status = next(
                category["status"]
                for category in result["category_analysis"]
                if category["category"] == item["category"]
            )
            self.assertNotEqual(category_status, "Good")
        self.assertNotIn("top_role", result)
        self.assertNotIn("recommended_roles", result)
        self.assertNotIn("recommendations", result)
        self.assertNotIn("next_steps", result)
        self.assertIsInstance(result["skills"], list)
        analyzer_output = str(
            {
                key: value
                for key, value in result.items()
                if key != "ml_prediction"
            }
        ).lower()
        self.assertNotIn("job description", analyzer_output)
        self.assertNotIn("role match", analyzer_output)


class ApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        prediction_patcher = patch(
            "services.analyzer.predict_category",
            return_value=FIXED_ML_PREDICTION,
        )
        prediction_patcher.start()
        self.addCleanup(prediction_patcher.stop)

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
