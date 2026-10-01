# Warranty Policy Files

Three configurable warranty-policy files are provided in **JSON** format:

| File | Product categories |
|------|--------------------|
| `policy_mobile_computing.json` | Mobile Phone, Laptop, Tablet, Smartphone |
| `policy_electronics.json` | TV, Camera, Printer, Monitor, Electronics |
| `policy_home_appliances.json` | Refrigerator, Washing Machine, Air Conditioner, Microwave |

The warranty rules are **data-driven**. They are loaded at runtime from these
files by `src/backend/rules/rule_engine.py` (`load_policy` → `evaluate_rules`).
No warranty rule is hard-coded throughout the application; changing a policy
file changes the behaviour without any code change or model retraining.

## Required fields (present in every policy)

| Field | Key in JSON | Meaning |
|-------|-------------|---------|
| Product category | `product_categories` | Categories this policy applies to |
| Coverage duration | `coverage_duration_months` | Allowed warranty lengths in months |
| Warranty start conditions | `warranty_start_conditions` | Start event, activation window, proof required |
| Covered faults | `covered_faults` | Fault types that are covered |
| Exclusions | `exclusions` | Excluded damage types and conditions |
| Claim-reporting period | `claim_reporting_period_days` | Days allowed between fault and claim |
| Repair conditions | `repair_conditions` | Authorized-only, max repairs, parts policy |
| Authorized service-centre requirements | `authorized_service_center` | Required flag, centre list, action |
| Replacement conditions | `replacement_conditions` | Max age, authorization, already-replaced rule |
| Grace periods | `grace_period_days` | Days after expiry still accepted |
| Mandatory documents | `mandatory_documents` | Documents required for a claim |
| Hard-fail rules | `hard_fail_rules` | Rules that force **Likely Invalid** |
| Warning rules | `warning_rules` | Rules that raise a warning |
| Manual-review rules | `manual_review_rules` | Rules that force **Manual Review Required** |

## How the rules are used

- **Hard-fail rules** (e.g. `warranty_expired`, `excluded_damage`) force a
  **Likely Invalid** decision regardless of the model outputs.
- **Warning rules** (e.g. `missing_document`, `serial_mismatch`) surface a
  warning to the user/reviewer.
- **Manual-review rules** (e.g. `date_contradiction`, `possible_duplicate`,
  `model_disagreement`, `low_confidence`) route the claim to the reviewer queue.

## Example (excerpt)

```json
{
  "policy_id": "policy_mobile_computing",
  "product_categories": ["Mobile Phone", "Laptop"],
  "coverage_duration_months": [12, 24],
  "grace_period_days": 5,
  "claim_reporting_period_days": 21,
  "mandatory_documents": ["purchase_receipt", "warranty_card", "product_photo", "serial_label_photo"],
  "hard_fail_rules": ["warranty_expired", "excluded_damage"],
  "warning_rules": ["missing_document", "serial_mismatch"],
  "manual_review_rules": ["date_contradiction", "possible_duplicate", "model_disagreement"]
}
```

The application-level policies (`src/` uses the same keys) and the dataset
policies share this schema, so a single policy set drives generation, rule
checking and evaluation consistently.
