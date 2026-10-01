# AI Tool Usage Declaration

**Project:** AssureX Claim Engine — AI-Based Warranty Claim Validation System
**Team:** TechWiz

This declaration lists every AI tool used during development, how it was used,
which files it affected, what the team changed and tested, and who verified the
output. It also states explicitly that the **final claim decision is produced
only by the team's own Python classification model, Google Teachable Machine
model, warranty-rule engine and application logic** — never by an external
generative-AI API.

> Summary: **AI was used mainly to train the data/models** (the classification
> models were trained on our own dataset) and as a coding/documentation
> assistant. No AI-generated content was submitted without the team reviewing,
> modifying, testing and understanding it.

---

## 1. AI / ML tools used for model training and data work

| AI tool | Purpose of use | Prompt / type of assistance | Files / modules affected | Modifications by team | Testing completed by team | Verified by |
|---------|----------------|-----------------------------|--------------------------|-----------------------|---------------------------|-------------|
| scikit-learn (RandomForest / XGBoost / LogisticRegression) | Train and compare the Python classification model on the structured claim dataset | "Train a 3-class classifier on the claim features and compare algorithms" | `ml_service/python_classifier.py`, `ml_service/models/python_claim_model.pkl` | Selected the final algorithm, tuned hyperparameters, added the preprocessing pipeline, wrote the metrics output | 5-fold cross-validation + held-out test; confusion matrix and per-class metrics reviewed | Abdul Rafay |
| TensorFlow / Keras (Google Teachable Machine format) | Train the Claim Summary Card image classifier | "Train an image classifier on the rendered summary cards" | `ml_service/train_tm_model.py`, `ml_service/models/teachable_machine.keras` | Defined card set, fixed class order, avoided horizontal flip, retrained after removing label leakage | Test accuracy measured on the held-out card split; predictions spot-checked | Veeraj Kumar Talerja |
| PyTorch + torchvision (ResNet18) | Alternative image model / transfer learning | "Fine-tune ResNet18 on the summary cards" | `ml_service/gtm_classifier.py`, `ml_service/models/gtm_cnn_model.pt` | Chose image size and augmentation, added early stopping, saved metrics | Test accuracy + confusion matrix reviewed; model loads and predicts | Veeraj Kumar Talerja |

## 2. AI assistant tools used for code and documentation

| AI tool | Purpose of use | Prompt / type of assistance | Files / modules affected | Modifications by team | Testing completed by team | Verified by |
|---------|----------------|-----------------------------|--------------------------|-----------------------|---------------------------|-------------|
| ChatGPT | Project structure and boilerplate; test ideas; documentation drafts | "Scaffold a FastAPI + React + SQLAlchemy warranty-claim app"; "suggest unit tests" | `backend/`, `frontend/`, `tests/`, docs | Rewrote routes, thresholds, evaluation flow and UI; changed schema and policies | Unit tests (pytest), API smoke tests, frontend build, manual end-to-end run | Abdul Rafay |
| Google Gemini | Summarising the requirements PDF into planning notes | "Summarise this requirements document" | Planning notes only | Used only for planning; no runtime dependency | Not applicable (planning only) | Hifza Azia |

## 3. AI-generated images

- The **Claim Summary Cards** are **not** AI-generated images. They are rendered
  programmatically with the Pillow library from claim facts
  (`dataset_generator/generate_summary_cards.py`, `generate_cards.py`).
- Any third-party sample photographs used in testing (for example stock damage
  photos) are used only as sample input documents and are declared here. No AI
  image generator was used to produce the decision or the summary cards.

## 4. Final decision is not AI-generated

The final decision (**Likely Valid / Likely Invalid / Manual Review Required**)
is produced entirely by the team's own components:

- `ml_service/python_classifier.py` — the trained Python tabular model,
- `ml_service/tm_classifier.py` / `gtm_classifier.py` — the Teachable Machine /
  image model,
- `backend/rules/rule_engine.py` — the configurable warranty-rule engine,
- `ml_service/decision_engine.py` — the application decision logic.

No external generative-AI API is called at any point to produce a claim
decision. Thresholds and policies live in `config/settings.json` and
`policies/*.json`, not in code.

## 5. Team declaration

We confirm that all AI-assisted output was independently reviewed, modified,
tested and understood before inclusion, and that the responsibility for the
final submission rests with the team.

| Team member | Role | Areas verified |
|-------------|------|----------------|
| Abdul Rafay | Team Lead | Backend, Python model, rules, AI-assisted code review |
| Hifza Azia | Service Center / Requirements | Requirements notes, policy files |
| Veeraj Kumar Talerja | Reviewer | Image models (TM / ResNet18), review workflow |
| Umer | Customer / Testing | End-to-end testing, UI flow |
