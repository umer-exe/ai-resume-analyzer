"""Train the optional Phase 6.5 resume category classifier."""

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BACKEND_DIR / "data" / "resume_dataset.csv"
MODEL_PATH = BACKEND_DIR / "models" / "resume_role_classifier.pkl"
RANDOM_STATE = 42

TEXT_COLUMN_CANDIDATES = ("Resume", "resume", "Resume_str", "text", "Text")
CATEGORY_COLUMN_CANDIDATES = (
    "Category",
    "category",
    "label",
    "Label",
)


def _find_column(columns, candidates):
    column_names = list(columns)

    for candidate in candidates:
        if candidate in column_names:
            return candidate

    normalized_columns = {
        str(column).strip().casefold(): column for column in column_names
    }
    for candidate in candidates:
        matched_column = normalized_columns.get(candidate.casefold())
        if matched_column is not None:
            return matched_column

    return None


def detect_dataset_columns(columns):
    """Return the supported resume text and category column names."""
    text_column = _find_column(columns, TEXT_COLUMN_CANDIDATES)
    category_column = _find_column(columns, CATEGORY_COLUMN_CANDIDATES)

    if text_column is None or category_column is None:
        raise ValueError(
            "Dataset must contain a resume text column and a category column"
        )

    return text_column, category_column


def load_dataset(dataset_path=DATASET_PATH):
    import pandas as pd

    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    dataset = pd.read_csv(dataset_path)
    text_column, category_column = detect_dataset_columns(dataset.columns)
    cleaned = dataset[[text_column, category_column]].dropna().copy()
    cleaned[text_column] = cleaned[text_column].astype(str).str.strip()
    cleaned[category_column] = cleaned[category_column].astype(str).str.strip()
    cleaned = cleaned[
        cleaned[text_column].ne("") & cleaned[category_column].ne("")
    ]

    if cleaned.empty:
        raise ValueError("Dataset has no usable resume and category rows")

    return cleaned[text_column], cleaned[category_column]


def train_and_select_model(resume_texts, categories):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    category_counts = categories.value_counts()
    stratify = categories if category_counts.min() >= 2 else None
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        resume_texts,
        categories,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    def build_pipeline(classifier):
        return Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        stop_words="english",
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.95,
                        max_features=30000,
                        sublinear_tf=True,
                    ),
                ),
                ("classifier", classifier),
            ]
        )

    models = {
        "Multinomial Naive Bayes": build_pipeline(MultinomialNB()),
        "Logistic Regression": build_pipeline(
            LogisticRegression(
                max_iter=1000,
                random_state=RANDOM_STATE,
            )
        ),
    }
    results = {}

    for model_name, pipeline in models.items():
        pipeline.fit(train_texts, train_labels)
        predictions = pipeline.predict(test_texts)
        results[model_name] = {
            "pipeline": pipeline,
            "accuracy": accuracy_score(test_labels, predictions),
            "predictions": predictions,
        }
        print(f"{model_name} accuracy: {results[model_name]['accuracy']:.4f}")

    selected_name = max(
        results,
        key=lambda name: results[name]["accuracy"],
    )
    selected_result = results[selected_name]

    print(f"\nSelected model: {selected_name}")
    print("\nClassification report:")
    print(
        classification_report(
            test_labels,
            selected_result["predictions"],
            zero_division=0,
        )
    )

    selected_pipeline = selected_result["pipeline"]
    selected_pipeline.fit(resume_texts, categories)
    return selected_name, selected_pipeline


def main():
    import joblib

    resume_texts, categories = load_dataset()
    print(f"Training rows: {len(resume_texts)}")
    print(f"Categories: {categories.nunique()}")

    selected_name, selected_pipeline = train_and_select_model(
        resume_texts,
        categories,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_pipeline, MODEL_PATH)
    print(f"Saved {selected_name} pipeline to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
