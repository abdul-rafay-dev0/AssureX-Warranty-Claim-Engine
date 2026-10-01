# Python Classification Model — Evidence Pack

Complete evidence for the **Python tabular classification model** of the
AssureX Claim Engine. The model classifies a warranty claim into
**Valid / Invalid / Manual Review** using structured claim features.

## Folder structure

```
Python Classification Model Evidence/
├─ README.md
├─ dataset/
│  ├─ train.csv                     structured training dataset
│  ├─ val.csv                       structured validation dataset
│  └─ test.csv                      structured testing dataset
├─ scripts/
│  ├─ preprocessing.py              data-preprocessing script
│  ├─ data_preprocessing.ipynb      data-preprocessing notebook
│  └─ training_script.py            model training script (python_classifier.py)
├─ documentation/
│  ├─ FEATURES.md                   feature descriptions
│  ├─ PREPROCESSING.md              feature engineering / missing values / encoding / scaling
│  ├─ ALGORITHMS.md                 algorithms tested + hyperparameters
│  └─ EVIDENCE.md                   all results (training, validation, testing, CV, metrics)
├─ results/
│  ├─ python_model_metrics.json     full training metrics
│  ├─ candidates_comparison.csv     the three algorithms compared
│  ├─ validation_results.json       hold-out validation results
│  ├─ cross_validation.json         5-fold cross-validation results
│  ├─ testing_results.json          test results
│  ├─ class_wise_performance.csv    precision/recall/F1 per class
│  ├─ confusion_matrix.csv          test confusion matrix
│  ├─ confusion_matrix.png          test confusion matrix image
│  ├─ feature_importance.csv        Random Forest feature importances
│  ├─ feature_importance.png        feature importance chart
│  └─ sample_test_predictions.csv   25 sample predictions with probabilities
└─ model/
   ├─ python_claim_model.pkl        saved Python model (full pipeline)
   ├─ preprocessor.pkl              fitted preprocessing pipeline (ColumnTransformer)
   ├─ label_encoder.pkl             label encoder
   ├─ label_classes.json            class list + integer encoding
   └─ model_version.json            model version metadata
```

## Model at a glance

| Item | Value |
|------|-------|
| Task | 3-class classification (Valid / Invalid / Manual Review) |
| Selected algorithm | Random Forest (best of three) |
| Algorithms compared | Random Forest, XGBoost, Logistic Regression |
| Test accuracy | **0.9630** |
| 5-fold CV accuracy (RF) | 0.9575 ± 0.0017 |
| Model version | 1.0.0 |
| Features | 15 (13 numeric + 2 categorical) |

See `documentation/EVIDENCE.md` for the full results.
