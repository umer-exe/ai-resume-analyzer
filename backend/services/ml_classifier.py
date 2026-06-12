"""Optional local ML category prediction for Phase 6.5."""

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = (BACKEND_DIR / "models" / "resume_role_classifier.pkl").resolve()

_loaded_model = None
_loaded_model_mtime = None


def _prediction_response(
    predicted_category=None,
    display_category=None,
    confidence=0,
    message=None,
):
    return {
        "predicted_category": predicted_category,
        "display_category": display_category,
        "confidence": confidence,
        "source": "ml_classifier",
        "message": message,
    }


def _display_category(category):
    return str(category).replace("_", " ").strip()


def _confidence_percentage(probabilities):
    if probabilities is None or len(probabilities) == 0:
        return 0

    confidence = round(float(max(probabilities)) * 100)
    return max(0, min(100, int(confidence)))


def _load_model():
    global _loaded_model, _loaded_model_mtime

    if not MODEL_PATH.is_file():
        _loaded_model = None
        _loaded_model_mtime = None
        return None

    model_mtime = MODEL_PATH.stat().st_mtime_ns
    if _loaded_model is None or _loaded_model_mtime != model_mtime:
        import joblib

        _loaded_model = joblib.load(MODEL_PATH)
        _loaded_model_mtime = model_mtime

    return _loaded_model


def predict_role(profile_text):
    """Predict a resume category without making model availability mandatory."""
    if not isinstance(profile_text, str) or not profile_text.strip():
        return _prediction_response(message="Profile text is required")

    try:
        normalized_text = profile_text.strip()
        model = _load_model()
        if model is None:
            return _prediction_response(message="ML model not trained yet")

        predicted_category = str(model.predict([normalized_text])[0]).strip()
        if not predicted_category:
            return _prediction_response(message="ML prediction is unavailable")

        confidence = 0

        if hasattr(model, "predict_proba"):
            confidence = _confidence_percentage(
                model.predict_proba([normalized_text])[0]
            )

        return _prediction_response(
            predicted_category=predicted_category,
            display_category=_display_category(predicted_category),
            confidence=confidence,
        )
    except Exception:
        return _prediction_response(message="ML prediction is unavailable")
