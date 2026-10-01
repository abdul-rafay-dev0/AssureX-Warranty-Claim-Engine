# tabular warranty claim classifier - trains 3 algorithms and saves the best one
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config.settings import MODEL_DIR, PROCESSED_DATA_DIR

TARGET = "class_label"
CLASSES = ["Invalid", "Manual_Review", "Valid"]
ID_COL = "claim_id"

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

MODEL_PATH = MODEL_DIR / "python_claim_model.pkl"
METRICS_PATH = MODEL_DIR / "python_model_metrics.json"
VERSION = "1.0.0"


# read train and test csv and split into features + labels
def load_data():
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train.csv")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test.csv")

    X_train = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = train_df[TARGET]
    X_test = test_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_test = test_df[TARGET]

    return X_train, X_test, y_train, y_test


# scales the numbers and one-hot encodes the text columns
def build_preprocessor() -> ColumnTransformer:
    pre = ColumnTransformer(
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
    return pre


# the 3 models we will try
def build_candidates() -> dict:
    candidates = {
        "RandomForest": Pipeline(
            [
                ("pre", build_preprocessor()),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=None,
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "XGBoost": Pipeline(
            [
                ("pre", build_preprocessor()),
                (
                    "clf",
                    _make_xgboost(),
                ),
            ]
        ),
        "LogisticRegression": Pipeline(
            [
                ("pre", build_preprocessor()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        ),
    }
    return candidates


# xgboost if it is installed, otherwise fall back to gradient boosting
def _make_xgboost():
    try:
        from xgboost import XGBClassifier

        # XGBoost requires integer class indices 0..n-1
        model = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
            tree_method="hist",
        )
        return model
    except ImportError:
        from sklearn.ensemble import GradientBoostingClassifier

        return GradientBoostingClassifier(random_state=42)


# turn class names into 0,1,2 for xgboost
def _encode(y: pd.Series) -> np.ndarray:
    mapping = {}
    for i, c in enumerate(CLASSES):
        mapping[c] = i
    return y.map(mapping).to_numpy()


# calculate accuracy / precision / recall / f1 for one run
def evaluate(y_true, y_pred, average: str = "weighted") -> dict:
    result = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=CLASSES).tolist(),
        "report": classification_report(y_true, y_pred, labels=CLASSES, zero_division=0),
    }
    return result


# main training routine
def train() -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    X_train, X_test, y_train, y_test = load_data()

    # small validation split from train for model selection
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.15, stratify=y_train, random_state=42
    )

    candidates = build_candidates()
    results = {}
    trained = {}

    for name, pipe in candidates.items():
        print(f"\nTraining {name}")

        # xgboost needs integer labels, the others use the strings directly
        if name == "XGBoost" and type(pipe.named_steps["clf"]).__name__ == "XGBClassifier":
            pipe.fit(X_tr, _encode(y_tr))
            val_pred_idx = pipe.predict(X_val)
            rev = {}
            for i, c in enumerate(CLASSES):
                rev[i] = c
            val_pred = pd.Series(val_pred_idx).map(rev)
            val_pred.index = y_val.index
        else:
            pipe.fit(X_tr, y_tr)
            val_pred = pipe.predict(X_val)

        metrics = evaluate(y_val, val_pred)
        results[name] = {
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "confusion_matrix": metrics["confusion_matrix"],
        }
        trained[name] = pipe
        print(f"  val accuracy={metrics['accuracy']:.4f}  f1={metrics['f1']:.4f}")

    # pick the model with the best validation accuracy (f1 breaks ties)
    best_name = None
    for name in results:
        if best_name is None:
            best_name = name
            continue
        if results[name]["accuracy"] > results[best_name]["accuracy"]:
            best_name = name
        elif results[name]["accuracy"] == results[best_name]["accuracy"]:
            if results[name]["f1"] > results[best_name]["f1"]:
                best_name = name
    best_pipe = trained[best_name]

    # retrain the winner on the full training set
    if best_name == "XGBoost" and type(best_pipe.named_steps["clf"]).__name__ == "XGBClassifier":
        best_pipe.fit(X_train, _encode(y_train))
        test_pred_idx = best_pipe.predict(X_test)
        rev = {}
        for i, c in enumerate(CLASSES):
            rev[i] = c
        test_pred = pd.Series(test_pred_idx).map(rev)
        test_pred.index = y_test.index
    else:
        best_pipe.fit(X_train, y_train)
        test_pred = best_pipe.predict(X_test)

    test_metrics = evaluate(y_test, test_pred)
    print(f"\nBest model: {best_name}")
    print(f"TEST accuracy={test_metrics['accuracy']:.4f}  "
          f"precision={test_metrics['precision']:.4f}  "
          f"recall={test_metrics['recall']:.4f}  "
          f"f1={test_metrics['f1']:.4f}")
    print(test_metrics["report"])

    # save the model file
    joblib.dump(best_pipe, MODEL_PATH)
    print(f"saved -> {MODEL_PATH}")

    # keep only the numbers for the json (report is a long string)
    test_nums = {}
    for k, v in test_metrics.items():
        if k != "report":
            test_nums[k] = v

    payload = {
        "version": VERSION,
        "best_algorithm": best_name,
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "classes": CLASSES,
        "candidates": results,
        "test_metrics": test_nums,
        "test_report": test_metrics["report"],
    }
    METRICS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"metrics -> {METRICS_PATH}")

    _record_model_version(best_name, test_metrics["accuracy"])
    return payload


# save a model version row in MySQL (skip if DB is not available)
def _record_model_version(algorithm: str, accuracy: float) -> None:
    try:
        from backend.database.connection import SessionLocal
        from backend.database.models import ModelType, ModelVersion

        db = SessionLocal()
        try:
            db.add(
                ModelVersion(
                    model_type=ModelType.python_tabular,
                    version=VERSION,
                    algorithm=algorithm,
                    accuracy=accuracy,
                    file_path=str(MODEL_PATH),
                )
            )
            db.commit()
            print("model version recorded in MySQL")
        finally:
            db.close()
    except Exception as exc:
        print(f"could not record model version: {exc}")


# inference API used by the decision engine

_pipeline = None


# load the saved model once and keep it in memory
def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run: python -m ml_service.python_classifier"
            )
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline


# predict one claim and return class + probabilities
def predict_python_model(feature_dict: dict) -> dict:
    pipe = _get_pipeline()

    # drop the id and label columns, keep only the features
    row = {}
    for k, v in feature_dict.items():
        if k != ID_COL and k != TARGET:
            row[k] = v
    X = pd.DataFrame([row])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

    clf = pipe.named_steps["clf"]
    if type(clf).__name__ == "XGBClassifier":
        # xgboost gives back integers so map them to class names
        idx = int(pipe.predict(X)[0])
        prediction = CLASSES[idx]
        proba = pipe.predict_proba(X)[0]
        probabilities = {}
        for i in range(len(CLASSES)):
            probabilities[CLASSES[i]] = float(proba[i])
    else:
        prediction = str(pipe.predict(X)[0])
        proba = pipe.predict_proba(X)[0]
        classes = list(pipe.named_steps["clf"].classes_)
        probabilities = {}
        for c, p in zip(classes, proba):
            probabilities[c] = float(p)
        # make sure all 3 classes are in the dict
        for c in CLASSES:
            if c not in probabilities:
                probabilities[c] = 0.0

    # confidence is just the probability of the predicted class
    confidence = probabilities.get(prediction, 0.0)
    rounded = {}
    for k, v in probabilities.items():
        rounded[k] = round(v, 4)

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "probabilities": rounded,
    }


if __name__ == "__main__":
    train()
