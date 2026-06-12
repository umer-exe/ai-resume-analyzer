import unittest
from unittest.mock import patch

from app import app
from ml.train_model import detect_dataset_columns
from services.analyzer import analyze_profile
from services.ml_classifier import predict_category


SAMPLE_PROFILE = "Python developer with Flask, SQL, and GitHub projects."


def fallback_prediction(message):
    return {
        "predicted_category": None,
        "display_category": None,
        "confidence": 0,
        "source": "ml_classifier",
        "message": message,
        "top_predictions": [],
    }


class FakeClassifier:
    classes_ = [
        "Data_Analyst",
        "Python_Developer",
        "Web_Developer",
        "Systems_Administrator",
    ]

    def predict(self, _profile_texts):
        return ["Python_Developer"]

    def predict_proba(self, _profile_texts):
        return [[0.08, 0.71, 0.16, 0.05]]


class MlClassifierTests(unittest.TestCase):
    def test_missing_model_returns_safe_fallback(self):
        with patch("services.ml_classifier._load_model", return_value=None):
            prediction = predict_category(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            fallback_prediction("ML model not trained yet"),
        )

    def test_empty_input_returns_safe_fallback(self):
        self.assertEqual(
            predict_category("   "),
            fallback_prediction("Profile text is required"),
        )

    def test_prediction_failure_returns_safe_fallback(self):
        with self.assertLogs("services.ml_classifier", level="ERROR"):
            with patch(
                "services.ml_classifier._load_model",
                side_effect=RuntimeError("model load failed"),
            ):
                prediction = predict_category(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            fallback_prediction("ML prediction is unavailable"),
        )

    def test_prediction_includes_display_category_and_top_predictions(self):
        with patch(
            "services.ml_classifier._load_model",
            return_value=FakeClassifier(),
        ):
            prediction = predict_category(SAMPLE_PROFILE)

        self.assertEqual(
            prediction,
            {
                "predicted_category": "Python_Developer",
                "display_category": "Python Developer",
                "confidence": 71,
                "source": "ml_classifier",
                "message": None,
                "top_predictions": [
                    {
                        "predicted_category": "Python_Developer",
                        "display_category": "Python Developer",
                        "confidence": 71,
                    },
                    {
                        "predicted_category": "Web_Developer",
                        "display_category": "Web Developer",
                        "confidence": 16,
                    },
                    {
                        "predicted_category": "Data_Analyst",
                        "display_category": "Data Analyst",
                        "confidence": 8,
                    },
                ],
            },
        )

    def test_analyzer_adds_ml_prediction_without_removing_phase6_fields(self):
        expected_prediction = {
            "predicted_category": "Python_Developer",
            "display_category": "Python Developer",
            "confidence": 72,
            "source": "ml_classifier",
            "message": None,
            "top_predictions": [],
        }

        with patch(
            "services.analyzer.predict_category",
            return_value=expected_prediction,
        ):
            result = analyze_profile(SAMPLE_PROFILE)

        phase6_fields = {
            "score",
            "status",
            "summary",
            "checks",
            "category_analysis",
            "skills",
            "action_plan",
        }
        self.assertTrue(phase6_fields.issubset(result))
        self.assertIsInstance(result["skills"], list)
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


class MlApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_valid_profile_still_returns_200_with_ml_prediction(self):
        with patch(
            "services.analyzer.predict_category",
            return_value=fallback_prediction("ML model not trained yet"),
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
        self.assertIn("top_predictions", ml_prediction)


if __name__ == "__main__":
    unittest.main()
