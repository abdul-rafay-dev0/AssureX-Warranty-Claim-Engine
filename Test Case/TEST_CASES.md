# Test Cases

Total test cases: **64** across 17 categories.


## Functional

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-FUNC-01 | User registration | Register a new customer with valid name/email/password | Account created, JWT returned, redirected to dashboard | PASS |
| TC-FUNC-02 | Login (all roles) | Login as customer, service_center, reviewer, admin | Each role lands on its own dashboard | PASS |
| TC-FUNC-03 | Product registration | Submit product form with name, category, serial, purchase details | Product stored and listed under Products | PASS |
| TC-FUNC-04 | Warranty registration | Set warranty duration/type while registering a product | Warranty row created with computed expiry; shown on Warranties page | PASS |
| TC-FUNC-05 | Claim creation wizard | Complete 5 wizard steps (Product, Fault, Documents, Review, Submit) | Claim created with code CLAIM-##### | PASS |
| TC-FUNC-06 | Document upload | Upload receipt, warranty card, damage photo, serial photo | Files saved, SHA-256 hashes stored, OCR preview shown | PASS |
| TC-FUNC-07 | Extracted-data verification | Edit an OCR field in step 4 | Correction saved and used as the verified source | PASS |
| TC-FUNC-08 | Dual-model evaluation | Click 'Run Dual-Model Evaluation' | Python + GTM predictions, match status and final decision displayed | PASS |
| TC-FUNC-09 | Claim status tracking | Open a claim after evaluation | Status badge reflects Submitted/Under Evaluation/Manual Review/Approved | PASS |
| TC-FUNC-10 | CSV export | Admin clicks 'Export CSV' | assurex_claims_export.csv downloaded | PASS |

## Integration

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-INT-01 | Health check | GET /api/health | api/database/models all report ok/true | PASS |
| TC-INT-02 | Auth -> product -> claim flow | Login, create product, create claim end to end | All API calls succeed with 200/201 | PASS |
| TC-INT-03 | Upload -> OCR -> evaluate | Upload files then evaluate | OCR text stored and evaluation returns a decision | PASS |
| TC-INT-04 | Reviewer override + audit | Reviewer overrides a decision | Claim updated and audit_logs row created | PASS |
| TC-INT-05 | Static upload serving | GET an uploaded file URL | File served from /uploads | PASS |

## Boundary

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-BND-01 | Remaining warranty = 0 | remaining_warranty_months = 0 | Treated as expired -> warranty_expired | PASS |
| TC-BND-02 | Remaining warranty = 1 | remaining_warranty_months = 1 | Not expired -> no warranty_expired | PASS |
| TC-BND-03 | Claim on purchase date | fault_date == claim_date == purchase_date | No contradiction | PASS |
| TC-BND-04 | Confidence exactly at threshold | top confidence = 0.60 | Classified per threshold rule (Uncertain below 0.60) | PASS |
| TC-BND-05 | Confidence difference exactly 0.10/0.20 | diff = 0.10 and 0.20 | Strong <=0.10, Acceptable <=0.20 | PASS |
| TC-BND-06 | Reporting exactly at deadline | lag == reporting_period_days | Within period (not late) | PASS |

## Negative

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-NEG-01 | Invalid file type | Upload a .exe file | Rejected with 'File type not allowed' | PASS |
| TC-NEG-02 | Oversized file | Upload > 10 MB | Rejected with 'File too large' | PASS |
| TC-NEG-03 | Fault date before purchase | fault_date < purchase_date | Rejected with clear validation message | PASS |
| TC-NEG-04 | Missing required claim fields | Submit claim without damage_type | 422 invalid/incomplete data | PASS |
| TC-NEG-05 | Unknown product id | Create claim for a non-existent product | 404 Product not found | PASS |

## Security

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-SEC-01 | Unauthenticated access | Call a protected endpoint without a token | 401 Unauthorized | PASS |
| TC-SEC-02 | Role-based access control | Customer calls an admin endpoint | 403 Forbidden | PASS |
| TC-SEC-03 | Cross-user claim access | Customer A opens Customer B's claim | 403 Forbidden | PASS |
| TC-SEC-04 | Password hashing | Inspect users table | password_hash only (pbkdf2_sha256), no plaintext | PASS |
| TC-SEC-05 | Path traversal in filename | Upload file named ../../evil.png | Filename sanitized; saved inside uploads dir | PASS |
| TC-SEC-06 | Expired/invalid JWT | Send a tampered token | 401 Invalid token | PASS |

## Database

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-DB-01 | Schema creation | Run python -m backend.database.init_db | 9 tables created | PASS |
| TC-DB-02 | Seed users/product | Run init_db | 4 demo users + 1 demo product seeded | PASS |
| TC-DB-03 | Unique serial constraint | Insert two products with the same serial | Unique constraint violation | PASS |
| TC-DB-04 | Cascade delete claim | Admin deletes a claim | Documents, repairs and audit rows removed | PASS |
| TC-DB-05 | JSON rule_findings stored | Evaluate a claim | rule_findings JSON persisted and reloaded | PASS |

## OCR

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-OCR-01 | Receipt text extraction | Upload a clear receipt image | Date, price, retailer, serial extracted | PASS |
| TC-OCR-02 | QR code decode | Upload a serial QR image | QR value decoded and appended to text | PASS |
| TC-OCR-03 | Low-quality image | Upload a blurred receipt | Partial/empty text; 'No OCR text' shown (no crash) | PASS |
| TC-OCR-04 | File hashing | Upload any file | SHA-256 hash computed and stored | PASS |

## Python Model

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-PY-01 | Prediction + confidences | Evaluate a claim | Predicted class + probabilities for all 3 classes | PASS |
| TC-PY-02 | Model file present | Check ml_service/models/python_claim_model.pkl | File loads and predicts | PASS |
| TC-PY-03 | Unknown category robustness | Predict with unseen product_category | No error (handle_unknown=ignore) | PASS |

## GTM

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-GTM-01 | Card classification | Classify a rendered summary card | Predicted class + 3 confidences | PASS |
| TC-GTM-02 | Model file present | Check ml_service/models/teachable_machine.keras | Model loads and predicts | PASS |
| TC-GTM-03 | Card has no label leakage | Inspect a rendered card | No class label / prediction printed on card | PASS |

## Model Comparison

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-CMP-01 | Match status computation | Both models agree closely | Strong Match | PASS |
| TC-CMP-02 | Confidence difference | Compute |conf_py - conf_gtm| | Delta computed and shown with threshold legend | PASS |
| TC-CMP-03 | Consistency statuses | Exercise all five statuses | Strong/Acceptable/Weak/Disagreement/Uncertain returned | PASS |

## Rule Engine

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-RULE-01 | Warranty active | remaining > 0 | warranty_expired NOT raised | PASS |
| TC-RULE-02 | Excluded damage | damage_type = liquid_damage | excluded_damage raised -> Likely Invalid | PASS |
| TC-RULE-03 | Policy loading per category | Load policy for Mobile/Electronics/Home Appliances | Correct policy JSON returned | PASS |
| TC-RULE-04 | Unauthorized repair | unauthorized_repair = 1 | unauthorized_repair raised | PASS |

## Contradiction

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-CONTRA-01 | Claim before purchase | claim_date < purchase_date | claim_date_before_purchase | PASS |
| TC-CONTRA-02 | Fault after claim | fault_date > claim_date | fault_date_after_claim | PASS |

## Missing Document

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-MISS-01 | Missing warranty card | Upload receipt only | missing_documents lists warranty_card; Manual Review | PASS |
| TC-MISS-02 | All documents present | Upload all mandatory docs | No missing_documents | PASS |

## Duplicate

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-DUP-01 | Duplicate document hash | Upload the same receipt twice | duplicate_document_hash raised | PASS |
| TC-DUP-02 | Duplicate serial claim | Two claims on the same serial | duplicate_serial_claim raised | PASS |

## Serial Mismatch

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-SERIAL-01 | Document serial differs | OCR serial != registered serial | serial_number_mismatch -> Manual Review | PASS |
| TC-SERIAL-02 | Unreadable serial photo | Serial photo unreadable | serial_number_unreadable -> Manual Review | PASS |

## Low Confidence

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-LOWCONF-01 | Top confidence < 0.60 | Both models low confidence | Uncertain Result -> Manual Review | PASS |

## Model Disagreement

| ID | Title | Steps | Expected Result | Status |
|----|-------|-------|-----------------|--------|
| TC-DISAGREE-01 | Different predictions | Python=Valid, GTM=Invalid | Model Disagreement -> Manual Review | PASS |