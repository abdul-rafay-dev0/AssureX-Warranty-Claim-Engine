# Required Scenario Demonstrations

The system demonstrates the following scenarios (see `scenario_evidence.csv`).

| # | Scenario | Setup | Expected Outcome | Result |
|---|----------|-------|------------------|--------|
| 1 | Valid claim | Active warranty, covered fault, all documents, serial matched | Likely Valid | ✅ |
| 2 | Invalid claim | Excluded damage (liquid damage) or policy violation | Likely Invalid | ✅ |
| 3 | Manual-review claim | Mixed/borderline signals requiring human judgement | Manual Review Required | ✅ |
| 4 | Expired-warranty claim | remaining_warranty_months <= 0 | Likely Invalid (hard-fail) | ✅ |
| 5 | Missing-document claim | A mandatory document not uploaded | Manual Review Required | ✅ |
| 6 | Duplicate claim | Same document hash / serial used before | Manual Review Required | ✅ |
| 7 | Contradictory claim | claim_date before purchase_date | Manual Review Required | ✅ |
| 8 | Serial-number mismatch | OCR serial != registered serial | Manual Review Required | ✅ |
| 9 | Unauthorized-repair claim | unauthorized_repair flag set | Manual Review Required / Invalid | ✅ |
| 10 | Tricky boundary-date claim | remaining warranty exactly 0 / claim on purchase date | Expired handled as boundary | ✅ |
| 11 | Model-disagreement case | Python and GTM predict different classes | Manual Review Required | ✅ |