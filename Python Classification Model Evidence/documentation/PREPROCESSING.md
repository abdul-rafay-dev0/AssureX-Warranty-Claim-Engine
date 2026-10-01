# Data Preprocessing & Feature Engineering

All preprocessing is implemented as a scikit-learn `Pipeline` so that the exact
same transformations are applied at training time and at serving time. The
pipeline is saved together with the classifier in `model/python_claim_model.pkl`.

## 1. Feature-engineering steps

1. **Derived numeric features** are computed from raw claim data:
   - `product_age_months` = months between purchase date and claim date.
   - `remaining_warranty_months` = warranty duration − product age.
   - `missing_document_count` = number of mandatory documents not uploaded.
2. **Document flags** are derived from the uploaded document types:
   `receipt_attached`, `warranty_card_attached`, `damage_photo_attached`,
   `serial_photo_attached` (each 0 or 1).
3. **Serial-match flag** `serial_number_match` is derived by comparing the
   registered serial number with the serial number read from documents (OCR/QR).
4. **Risk flags** `contradiction_flag` and `duplicate_flag` are set by the
   contradiction checker and the duplicate detector.
5. **Repair features** `repair_history_count` and `unauthorized_repair_flag`
   come from the claim's repair records.

## 2. Missing-value handling method

- Numeric fields default to `0` where a value is not applicable (for example
  `repair_history_count` and the attachment flags).
- `remaining_warranty_months` falls back to `0` when no warranty record exists.
- Categorical fields have safe defaults (`product_category` defaults to
  `Electronics`, `fault_type` defaults to `other`).
- Because the pipeline is trained on a fully populated dataset, the model does
  not use an imputer; defaults are applied during feature assembly so that the
  feature vector is always complete. `OneHotEncoder(handle_unknown="ignore")`
  also prevents errors when an unseen category appears.

## 3. Categorical encoding method

- `product_category` and `fault_type` are encoded with
  **`OneHotEncoder(handle_unknown="ignore", sparse_output=False)`**.
- Unknown categories encountered at inference are encoded as all-zeros instead
  of raising an error, which keeps the service robust to new product categories.
- The target label is kept as the original class string for Random Forest and
  Logistic Regression; for XGBoost the three classes are mapped to integer
  indices `0..2` (`label_encoder.pkl`, `label_classes.json`).

## 4. Numerical scaling / normalisation method

- All 13 numeric features are standardised with **`StandardScaler`**
  (zero mean, unit variance), fitted on the training data.
- Scaling is required by Logistic Regression and harmless for tree-based
  models, so a single shared preprocessor is used for all three algorithms.

## 5. The preprocessing pipeline

```
ColumnTransformer
├─ ("num", StandardScaler(), [13 numeric features])
└─ ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
          ["product_category", "fault_type"])
```

The fitted `ColumnTransformer` is saved separately as
`model/preprocessor.pkl` and its output feature names are available through
`preprocessor.get_feature_names_out()`.

## 6. Train / validation / test protocol

- The structured dataset is split **70 / 15 / 15** (train / validation / test)
  with stratification on the class label.
- A further 15% stratified slice of the training set is used for **model
  selection**; the winning model is then retrained on the full training set.
- The test set is untouched during training and model selection.

See `scripts/preprocessing.py` and `scripts/data_preprocessing.ipynb` for the
runnable implementation.
