# Algorithms Tested & Hyperparameter Settings

Three suitable classification algorithms were trained and compared under
**identical preprocessing** before selecting the final model, as required.

## 1. Random Forest (selected)

| Hyperparameter | Value |
|----------------|-------|
| n_estimators | 300 |
| max_depth | None |
| class_weight | balanced |
| random_state | 42 |
| n_jobs | -1 |

Chosen because it gave the best validation accuracy and robust probability
estimates, and it tolerates unscaled/mixed features well.

## 2. XGBoost

| Hyperparameter | Value |
|----------------|-------|
| n_estimators | 300 |
| max_depth | 6 |
| learning_rate | 0.08 |
| subsample | 0.9 |
| colsample_bytree | 0.9 |
| objective | multi:softprob |
| eval_metric | mlogloss |
| tree_method | hist |
| random_state | 42 |

A very close second; slightly behind Random Forest on validation accuracy.

## 3. Logistic Regression

| Hyperparameter | Value |
|----------------|-------|
| max_iter | 2000 |
| class_weight | balanced |
| random_state | 42 |

The simplest baseline; strong performance confirms the engineered features are
highly informative.

## Common settings

- **Preprocessing (shared):** `StandardScaler` on numeric features +
  `OneHotEncoder(handle_unknown="ignore")` on categorical features.
- **Model selection:** a 15% stratified slice of the training data.
- **Final evaluation:** retrained on the full training set, evaluated on the
  held-out test set.
- **Class labels:** kept as strings for Random Forest / Logistic Regression;
  integer-encoded (`0..2`) for XGBoost.

## Selection outcome

Random Forest was selected as the final model. Full comparison numbers are in
`results/candidates_comparison.csv` and `documentation/EVIDENCE.md`.
