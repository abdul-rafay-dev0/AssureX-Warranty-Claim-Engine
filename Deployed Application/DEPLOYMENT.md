# Deployed Application

AssureX Claim Engine — public deployment details.

> **Sample values below.** Replace the URL and credentials with your real
> deployment before submitting.

## 1. Public application URL

```
https://sfcbitpy.odinno.com
```

- Frontend: `https://sfcbitpy.odinno.com`

## 2. Evaluator login credentials

| Role | Email | Password |
|------|-------|----------|
| Customer | umer@gmail.com | Password@123 |
| Service Center | hifza@gmail.com | Password@123 |
| Reviewer | veeraj@gmail.com | Password@123 |

## 3. Administrator login credentials

| Role | Email | Password |
|------|-------|----------|
| Administrator | abdulrafay.dev00@gmail.com | Password@123 |

> Change the default admin password on a real deployment.

## 4. Sample claim records

| Sample | Claim ID | Scenario | Expected outcome |
|--------|----------|----------|------------------|
| Valid claim | CLAIM-00001 | Active warranty, covered fault, all documents | Likely Valid |
| Invalid claim | CLAIM-00002 | Excluded damage / expired warranty | Likely Invalid |
| Manual-review claim | CLAIM-00003 | Missing document or serial mismatch | Manual Review Required |
| Model-disagreement case | CLAIM-00004 | Python and GTM predict different classes | Manual Review Required |

Ready-made JSON samples are in `sample_claims/valid_claim.json` and
`sample_claims/invalid_claim.json`.

## 5. Instructions for testing the application

1. Open the public URL and log in as the **Customer** (umer@gmail.com).
2. Go to **Products → Register new product** and register a product with a
   serial number and warranty duration.
3. Go to **New Claim**, complete the wizard: pick the product, enter fault
   details, **upload a receipt, warranty card, damage photo and serial photo**.
4. On the **Review Data** step, verify/correct the OCR-extracted fields, then
   **Submit**.
5. Click **Run Dual-Model Evaluation** and observe:
   - Python prediction + confidence (left panel),
   - GTM prediction + confidence (right panel),
   - Match status and confidence difference,
   - Decision explanation (rules passed/failed, contradictions, duplicates),
   - The generated Claim Summary Card.
6. Log in as the **Reviewer** (veeraj@gmail.com), open **Reviewer Queue**, and
   override a decision to see the audit trail.
7. Log in as the **Administrator** (abdulrafay.dev00@gmail.com), open
   **Analytics**, and click **Export CSV**.

## 6. Local fallback (if public deployment is not possible)

If a public URL is unavailable, provide the local installation and run steps
from `Installation Instruction/INSTALL.md` and
`Execution Instruction/README.md`, together with the demonstration video.

```bash
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev      # http://localhost:5174/
```
