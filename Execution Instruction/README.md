# Execution Instructions

AssureX Claim Engine — how to run and use the application, step by step.

**Frontend:** http://localhost:5174/  ·  **API docs:** http://127.0.0.1:8000/docs

---

## 1. How to install the application

See `Installation Instruction/INSTALL.md`. In short:

```bash
pip install -r requirements.txt
python -m backend.database.init_db
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000   # terminal 1
cd frontend && npm install && npm run dev                            # terminal 2
```

Open http://localhost:5174/.

## 2. How to register or log in

- Go to **http://localhost:5174/login** to sign in, or click **Register**
  (http://localhost:5174/register) to create an account.
- Demo logins: admin `abdulrafay.dev00@gmail.com`, customer `umer@gmail.com`,
  service center `hifza@gmail.com`, reviewer `veeraj@gmail.com` — all with
  password `Password@123`.
- After login you are routed to the dashboard for your role.

## 3. How to register a product

- Open **Products → Register new product** (http://localhost:5174/products/new).
- Fill in product name, category, brand, model number, **serial number**,
  purchase date, price and retailer.
- Save. The product now appears on the Products page and can be selected in the
  claim wizard.

## 4. How to add warranty information

- Warranty details are entered on the same product form: **warranty duration
  (months)** and **warranty type (standard/extended)**.
- The system computes the warranty start and expiry dates automatically.
- View all warranties on the **Warranties** page
  (http://localhost:5174/warranties), which shows active, nearing-expiry and
  expired warranties.

## 5. How to create a claim

- Open **New Claim** (http://localhost:5174/claims/new).
- The wizard has five steps: **Product → Fault Details → Documents → Review
  Data → Submit**.
- Step 1: pick the registered product.
- Step 2: enter the fault date, claim date, damage type, fault type and any
  repair history.

## 6. How to upload documents

- In wizard **step 3 (Documents)** upload the receipt, warranty card, damage
  photo and serial photo (optional extras: product photo, fault video,
  diagnostic report, other evidence).
- Each file is saved under `uploads/` and hashed with SHA-256; an **OCR / upload
  preview** panel confirms the upload.

## 7. How to verify extracted information

- In wizard **step 4 (Review Data)** the fields read from your documents are
  shown: product name, model number, serial number, invoice number, purchase
  date, retailer, price and warranty months.
- Correct anything that is wrong. Corrected values take priority over raw OCR.
- A "Before you submit" box lists warnings and recommendations.

## 8. How to submit a claim

- In wizard **step 5** click **Submit** (then **Run Dual-Model Evaluation**).
- The claim gets a code such as `CLAIM-00042` and opens on the claim page.

## 9. How to generate the Python prediction

- On the claim page (http://localhost:5174/claims/:id) click **Run Dual-Model
  Evaluation**.
- The **Dual-model comparison** card shows the Python prediction in the left
  panel **"Python · Tabular"**.

## 10. How to interpret Python confidence scores

- The Python model returns a confidence for **all three classes** (Valid,
  Invalid, Manual Review). The winning class confidence is shown under the
  prediction; the full probability vector is returned by the evaluate API and
  shown in the confidence meter.
- Higher confidence means the model is more certain. The top confidence is also
  used to detect "Uncertain Result" (below 0.60).

## 11. How to generate the Claim Summary Card

- The card is generated automatically during evaluation and shown in the
  **"Summary card (GTM input)"** card on the claim page.
- It is also saved to `uploads/summary_cards/<CLAIM-CODE>.png`. The card shows
  claim facts only — never the prediction or label.

## 12. How to obtain the Google Teachable Machine prediction

- In the same **Dual-model comparison** card, the right panel
  **"GTM · Summary card"** shows the Teachable Machine prediction and its
  confidence. It reads the summary card rendered in step 11.

## 13. How to compare both model results

- The two panels sit side by side. The **Match status** badge shows
  **Strong Match / Acceptable Match / Weak Match / Model Disagreement /
  Uncertain Result**.
- The **Confidence difference (Δ)** row shows the absolute difference between
  the two top-class confidences, with the threshold legend
  (Strong ≤0.10 · Acceptable ≤0.20).

## 14. How to review warranty-rule results

- The **Decision explanation** card lists **Rules passed** and failed rules, and
  the **Supporting** and **Opposing** factors. Rules come from the category
  policy files in `policies/`.

## 15. How to check contradictions

- Contradictions appear as chips in the **Decision explanation** card (for
  example `claim_date_before_purchase`, `serial_number_mismatch`).
- The **Document verification** card compares the registered value against the
  value read from the document (serial, purchase date, price, retailer).

## 16. How to identify duplicate claims

- Duplicate indicators appear as chips in the **Decision explanation** card
  (for example `duplicate_document_hash`, `duplicate_serial_claim`).
- The admin dashboard shows a **Duplicate alerts** counter.

## 17. How to access the manual-review queue

- Sign in as reviewer/admin and open **Reviewer Queue**
  (http://localhost:5174/reviewer).
- Use the **Manual review** filter. Claims with model disagreement, low
  confidence, missing evidence or contradictions appear here.
- Open a claim with **Open workspace** to review and override.

## 18. How to access the administrator dashboard

- Sign in as admin and open **Analytics** (http://localhost:5174/admin).
- See KPI cards, claim trends, decision and fault charts, the monitoring panel,
  user and file tables, and the expiry-alert setting.

## 19. How to track claim status

- Status badges appear on the **Claims** list and the claim page: Draft,
  Submitted, Under Evaluation, Additional Info Required, Manual Review,
  Approved, Rejected, Closed.

## 20. How to export a claim report

- On the admin dashboard click **Export CSV** (endpoint
  `/api/admin/export/claims.csv`). The file `assurex_claims_export.csv`
  downloads with claim details, model results, confidences and final decision.

## 21. How to run automated tests

```bash
python -m pytest tests -q        # unit tests (rule engine, decision engine)
python tests/smoke_phase6.py     # API smoke tests (server must be running)
cd frontend && npm run build     # frontend build check
```
