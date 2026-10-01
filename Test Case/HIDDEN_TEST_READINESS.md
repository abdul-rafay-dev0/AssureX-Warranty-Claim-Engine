# Hidden-Test Readiness Checklist

Before evaluation, confirm every item below.

## Environment
- [ ] Python 3.10+ installed; `pip install -r requirements.txt` succeeds
- [ ] MySQL running; `python -m backend.database.init_db` completes
- [ ] Tesseract OCR installed and on PATH (or at the configured path)
- [ ] Model files present in `ml_service/models/` (`python_claim_model.pkl`,
      `teachable_machine.keras`, `gtm_cnn_model.pt`)
- [ ] Backend health check returns all `true` at `/api/health`

## Functional
- [ ] All four demo logins work
- [ ] Product, warranty and claim creation work end to end
- [ ] Document upload + OCR extraction work
- [ ] Extracted-data correction is honoured
- [ ] Dual-model evaluation returns a decision

## Models
- [ ] Python model returns 3 class probabilities
- [ ] GTM model classifies the summary card
- [ ] Match status, confidence difference and consistency status are shown
- [ ] At least one model-disagreement case routes to manual review

## Rules & detection
- [ ] Warranty expiry, excluded damage and reporting rules run from policy files
- [ ] Missing documents are listed
- [ ] Contradictions are detected
- [ ] Duplicates (hash / serial / description) are detected
- [ ] Serial-number mismatch routes to manual review

## Review & reporting
- [ ] Manual-review queue lists flagged claims
- [ ] Reviewer override writes to the audit trail
- [ ] Admin dashboard charts load
- [ ] CSV export downloads

## Tests
- [ ] `python -m pytest tests -q` passes
- [ ] `python tests/smoke_phase6.py` passes (server running)
- [ ] `npm run build` in `frontend/` succeeds
