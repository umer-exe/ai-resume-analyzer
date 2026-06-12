import unittest
from unittest.mock import patch

from app import app
from ml.train_model import detect_dataset_columns
from services.analyzer import analyze_profile
from services.ml_classifier import predict_role


SAMPLE_PROFILE = "Python developer with Flask, SQL, and GitHub projects."


class FakeClassifier:
    def predict(self, _profile_texts):
        return ["Python_Developer"]

    def predict_proba(self, _profile_texts):
        return [[0.14, 0.86]]


class MlClassifierTests(unittest.TestCase):
    def test_missing_model_returns_safe_fallback(self):
        with patch("services.ml_classifier._load_model", return_value=None):
            prediction = predict_role(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            {
                "predicted_category": None,
                "display_category": None,
                "confidence": 0,
                "source": "ml_classifier",
                "message": "ML model not trained yet",
            },
        )

    def test_empty_input_returns_safe_fallback(self):
        self.assertEqual(
            predict_role("   "),
            {
                "predicted_category": None,
                "display_category": None,
                "confidence": 0,
                "source": "ml_classifier",
                "message": "Profile text is required",
            },
        )

    def test_prediction_failure_returns_safe_fallback(self):
        with patch(
            "services.ml_classifier._load_model",
            side_effect=RuntimeError("model load failed"),
        ):
            prediction = predict_role(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            {
                "predicted_category": None,
                "display_category": None,
                "confidence": 0,
                "source": "ml_classifier",
                "message": "ML prediction is unavailable",
            },
        )

    def test_prediction_includes_display_category_and_bounded_confidence(self):
        with patch(
            "services.ml_classifier._load_model",
            return_value=FakeClassifier(),
        ):
            prediction = predict_role(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            {
                "predicted_category": "Python_Developer",
                "display_category": "Python Developer",
                "confidence": 86,
                "source": "ml_classifier",
                "message": None,
            },
        )

    def test_analyzer_adds_ml_prediction_without_removing_phase6_fields(self):
        expected_prediction = {
            "predicted_category": "Python_Developer",
            "display_category": "Python Developer",
            "confidence": 72,
            "source": "ml_classifier",
            "message": None,
        }

        with patch(
            "services.analyzer.predict_role",
            return_value=expected_prediction,
        ):
            result = analyze_profile(SAMPLE_PROFILE)

        phase6_fields = {
            "score",
            "status",
            "summary",
            "top_role",
            "checks",
            "category_analysis",
            "skills",
            "recommended_roles",
            "recommendations",
            "next_steps",
        }
        self.assertTrue(phase6_fields.issubset(result))
        self.assertEqual(result["ml_prediction"], expected_prediction)

    def test_supported_dataset_columns_are_detected(self):
        self.assertEqual(
            detect_dataset_columns(["Resume", "Category"]),
            ("Resume", "Category"),
        )
        self.assertEqual(
            detect_dataset_columns(["Resume_str", "label"]),
            ("Resume_str", "label"),
        )
        self.assertEqual(
            detect_dataset_columns([" Text ", " LABEL "]),
            (" Text ", " LABEL "),
        )


class Phase65ApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_valid_profile_still_returns_200_with_ml_prediction(self):
        with patch(
            "services.analyzer.predict_role",
            return_value={
                "predicted_category": None,
                "display_category": None,
                "confidence": 0,
                "source": "ml_classifier",
                "message": "ML model not trained yet",
            },
        ):
            response = self.client.post(
                "/api/v1/analyze",
                data={"profile_text": SAMPLE_PROFILE},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        ml_prediction = response.get_json()["data"]["ml_prediction"]
        self.assertEqual(ml_prediction["source"], "ml_classifier")
        self.assertIn("display_category", ml_prediction)


if __name__ == "__main__":
    unittest.main()
