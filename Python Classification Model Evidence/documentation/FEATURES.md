# Feature Descriptions

The Python classification model uses **15 input features** — 13 numeric and 2
categorical — and predicts one of three classes: **Valid**, **Invalid** or
**Manual_Review**.

## Numeric features (13)

| # | Feature | Type | Description |
|---|---------|------|-------------|
| 1 | product_age_months | int | Age of the product in months at claim time. |
| 2 | warranty_duration_months | int | Total warranty length in months. |
| 3 | remaining_warranty_months | int | Months of warranty left (≤ 0 means expired). |
| 4 | purchase_price | float | Purchase price of the product. |
| 5 | repair_history_count | int | Number of previous repairs on the product. |
| 6 | unauthorized_repair_flag | 0/1 | 1 if an unauthorized repair centre was used. |
| 7 | serial_number_match | 0/1 | 1 if the document serial matches the registered serial. |
| 8 | receipt_attached | 0/1 | 1 if a purchase receipt was uploaded. |
| 9 | warranty_card_attached | 0/1 | 1 if a warranty card was uploaded. |
| 10 | damage_photo_attached | 0/1 | 1 if a damage photo was uploaded. |
| 11 | serial_photo_attached | 0/1 | 1 if a serial-number photo was uploaded. |
| 12 | contradiction_flag | 0/1 | 1 if any contradiction was detected. |
| 13 | duplicate_flag | 0/1 | 1 if any duplicate indicator was detected. |

## Categorical features (2)

| # | Feature | Values |
|---|---------|--------|
| 14 | product_category | Electronics, Home Appliances, Mobile, … |
| 15 | fault_type | display_defect, battery_failure, motor_failure, liquid_damage, physical_impact, intermittent_fault, … |

## Target variable

| Feature | Type | Values |
|---------|------|--------|
| class_label | category | Valid, Invalid, Manual_Review |

## Why these features

The features fall into four groups that mirror how a human assessor reasons:

1. **Warranty status** — `product_age_months`, `warranty_duration_months`,
   `remaining_warranty_months` capture whether the product is still covered.
2. **Fault / damage nature** — `fault_type`, `unauthorized_repair_flag`
   capture whether the reported fault is the kind a policy covers.
3. **Evidence completeness** — `receipt_attached`, `warranty_card_attached`,
   `damage_photo_attached`, `serial_photo_attached`, `serial_number_match`
   capture whether the claimant provided verifiable proof.
4. **Risk / fraud signals** — `repair_history_count`, `contradiction_flag`,
   `duplicate_flag` capture behaviour associated with invalid or fraudulent claims.

`purchase_price` is kept as a weak signal of product class and claim size.

## Feature importance (Random Forest)

Top features by Gini importance (see `results/feature_importance.csv`):

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

The three strongest signals — repair history, remaining warranty and
unauthorized repair — align exactly with the business rules, which is a good
sign that the model learned meaningful structure rather than noise.
