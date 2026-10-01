# Model Evaluation Evidence

Selected model: **Random Forest** (best of three algorithms). All numbers below
come from the saved artefacts in `results/`.

## 1. Algorithms compared (hold-out validation, 15% of training data)

| Algorithm | Accuracy | Precision | Recall | F1 |
|-----------|----------|-----------|--------|-----|
| **Random Forest** | **0.9605** | 0.9604 | 0.9605 | 0.9602 |
| XGBoost | 0.9586 | 0.9585 | 0.9586 | 0.9583 |
| Logistic Regression | 0.9514 | 0.9517 | 0.9514 | 0.9511 |

Random Forest was selected and retrained on the full training set.

## 2. 5-fold cross-validation (on the training set)

| Algorithm | Mean accuracy | Std | Mean F1 (weighted) |
|-----------|---------------|-----|--------------------|
| **Random Forest** | **0.9575** | 0.0017 | 0.9572 |
| XGBoost | 0.9576 | 0.0020 | 0.9574 |
| Logistic Regression | 0.9515 | 0.0020 | 0.9512 |

The very small standard deviations show the results are stable across folds.
(Per-fold accuracies are in `results/cross_validation.json`.)

## 3. Testing results (held-out test set, 3,001 claims)

| Metric | Value |
|--------|-------|
| Accuracy | **0.9630** |
| Precision (weighted) | 0.9630 |
| Recall (weighted) | 0.9630 |
| F1-score (weighted) | 0.9628 |

## 4. Confusion matrix (test set)

Rows = actual, columns = predicted. Order: Invalid, Manual_Review, Valid.

| | Invalid | Manual_Review | Valid |
|--|--|--|--|
| **Invalid** | 962 | 0 | 0 |
| **Manual_Review** | 35 | 965 | 33 |
| **Valid** | 0 | 43 | 963 |

See `results/confusion_matrix.png`. Invalid and Valid are almost perfectly
separated; the small residual errors are concentrated in the deliberately
ambiguous Manual_Review class.

## 5. Class-wise performance (test set)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| Invalid | 0.965 | 1.000 | 0.982 | 962 |
| Manual_Review | 0.957 | 0.934 | 0.946 | 1,033 |
| Valid | 0.967 | 0.957 | 0.962 | 1,006 |
| **Macro avg** | 0.963 | 0.964 | 0.963 | 3,001 |
| **Weighted avg** | 0.963 | 0.963 | 0.963 | 3,001 |

Manual_Review has the lowest recall (0.934) because it is intentionally the
hardest, boundary class.

## 6. Feature-importance analysis

Random Forest Gini importances (top 10; full list in
`results/feature_importance.csv`, chart in `results/feature_importance.png`):

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | repair_history_count | 0.157 |
| 2 | remaining_warranty_months | 0.136 |
| 3 | unauthorized_repair_flag | 0.135 |
| 4 | product_age_months | 0.053 |
| 5 | warranty_card_attached | 0.050 |
| 6 | contradiction_flag | 0.044 |
| 7 | purchase_price | 0.042 |
| 8 | fault_type = intermittent_fault | 0.036 |
| 9 | duplicate_flag | 0.034 |
| 10 | fault_type = screen_flicker | 0.031 |

The strongest features match the warranty business rules, indicating the model
learned meaningful structure.

## 7. Sample test predictions

`results/sample_test_predictions.csv` contains 25 test claims with the actual
label, the predicted label, the probability of each of the three classes, and a
correct/incorrect flag. Example:

| claim_id | actual_label | predicted_label | prob_Invalid | prob_Manual_Review | prob_Valid | correct |
|----------|--------------|-----------------|--------------|--------------------|------------|---------|
| CLM-… | Valid | Valid | 0.00 | 0.04 | 0.96 | True |

## 8. Artefacts

| Artefact | File |
|----------|------|
| Saved model (full pipeline) | `model/python_claim_model.pkl` |
| Preprocessing pipeline | `model/preprocessor.pkl` |
| Label encoder | `model/label_encoder.pkl` |
| Class list / encoding | `model/label_classes.json` |
| Model version | `model/model_version.json` |
| Full metrics | `results/python_model_metrics.json` |
