"""Data preprocessing for the AssureX Python classification model.

Builds and demonstrates the scikit-learn preprocessing pipeline used before
training: numeric standardisation + one-hot encoding of categorical features.
Run:  python scripts/preprocessing.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---- feature definition (must match ml_service/python_classifier.py) ----
NUMERIC_FEATURES = [
    "product_age_months",
    "warranty_duration_months",
    "remaining_warranty_months",
    "purchase_price",
    "repair_history_count",
    "unauthorized_repair_flag",
    "serial_number_match",
    "receipt_attached",
    "warranty_card_attached",
    "damage_photo_attached",
    "serial_photo_attached",
    "contradiction_flag",
    "duplicate_flag",
]
CATEGORICAL_FEATURES = ["product_category", "fault_type"]
TARGET = "class_label"


def build_preprocessor() -> ColumnTransformer:
    """Standardise numeric features and one-hot encode categorical features."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )


def build_pipeline(classifier) -> Pipeline:
    """Preprocessing + classifier as a single serialisable pipeline."""
    return Pipeline([("pre", build_preprocessor()), ("clf", classifier)])


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values with safe defaults so the feature vector is complete."""
    df = df.copy()
    for c in NUMERIC_FEATURES:
        if c in df.columns:
            df[c] = df[c].fillna(0)
    if "product_category" in df.columns:
        df["product_category"] = df["product_category"].fillna("Electronics")
    if "fault_type" in df.columns:
        df["fault_type"] = df["fault_type"].fillna("other")
    return df


def main() -> None:
    here = Path(__file__).resolve().parent.parent
    train = pd.read_csv(here / "dataset" / "train.csv")
    train = handle_missing(train)

    X = train[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    pre = build_preprocessor()
    Xt = pre.fit_transform(X)

    print(f"input features : {X.shape[1]}")
    print(f"output features: {Xt.shape[1]}")
    print("output feature names:")
    for name in pre.get_feature_names_out():
        print("  -", name)


if __name__ == "__main__":
    main()
