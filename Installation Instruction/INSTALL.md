# Installation Instructions

AssureX Claim Engine — complete setup guide.

## 1. Prerequisite software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ (tested on 3.13) | Backend, ML service, scripts |
| Node.js + npm | 18+ (tested on 22) | React frontend |
| MySQL | 8.0 (XAMPP recommended) | Database |
| Tesseract OCR | 5.x (optional but recommended) | Receipt/document OCR |
| Git | any | Clone the repository |

## 2. Supported operating system

- **Windows 10/11** (primary, tested)
- **Linux / macOS** (works; update the Tesseract and font paths)

## 3. Required Python version

Python **3.10 or newer**. Check with:

```bash
python --version
```

## 4. Virtual-environment creation steps

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

## 5. Dependency installation steps

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` includes FastAPI, Uvicorn, SQLAlchemy, PyMySQL, pandas,
scikit-learn, xgboost, torch, torchvision, tensorflow, pillow, opencv,
pytesseract and pytest.

For the frontend:

```bash
cd frontend
npm install
cd ..
```

## 6. Database configuration

1. Start **MySQL** (XAMPP Control Panel → Start MySQL, port 3306).
2. Default credentials are `root` with an empty password.
3. Configure them in `.env` (see section 11).

## 7. Database initialization / seed steps

```bash
python -m backend.database.init_db
```

This creates the `assurex_db` database, creates the 9 tables, runs small
migrations, and seeds 4 demo users and 1 demo product.

## 8. Model placement instructions

Place the trained model files in `ml_service/models/`:

| File | Description |
|------|-------------|
| `python_claim_model.pkl` | Python tabular model (scikit-learn pipeline) |
| `gtm_cnn_model.pt` | PyTorch ResNet18 image model (fallback) |
| `labels.txt` | Class labels for the PyTorch model |
| `python_model_metrics.json` | Python model metrics |

If the files are missing, retrain them:

```bash
python -m ml_service.python_classifier
python -m ml_service.gtm_classifier
```

## 9. Google Teachable Machine model placement

Export the image model from Teachable Machine (Keras or TensorFlow Lite) and
place it in `ml_service/models/`:

| File | Description |
|------|-------------|
| `teachable_machine.keras` | Teachable Machine exported model (Keras) |
| `teachable_machine_labels.txt` | Class labels, one per line |

The application automatically prefers `teachable_machine.keras` when present.
To train a local equivalent: `python -m ml_service.train_tm_model`.

## 10. OCR installation and configuration

1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Default path on Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. The path is configured in `backend/ocr/document_parser.py`
   (`TESSERACT_PATHS`). If Tesseract is on the system PATH, no change is needed.
4. Without Tesseract the app still runs; OCR text extraction is skipped.

## 11. Environment-variable configuration

Edit `.env` in the project root:

```
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=assurex_db

SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 12. Folder setup

```
backend/        FastAPI routes, models, rules, OCR, services
frontend/       React app (src/)
ml_service/     models + decision engine (models/ holds the model files)
dataset_generator/  synthetic data + summary-card generation
config/         settings.py + settings.json
policies/       warranty policy JSON files
data/           CSVs + summary card images
uploads/        uploaded files (receipts, evidence, summary cards)
tests/          pytest + smoke tests
```

Create the runtime folders if they do not exist:

```bash
mkdir uploads\receipts uploads\evidence uploads\summary_cards
```

## 13. Application execution command

Backend (terminal 1):

```bash
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
```

Frontend (terminal 2):

```bash
cd frontend
npm run dev
```

Open **http://localhost:5174/**. API docs: http://127.0.0.1:8000/docs

## 14. Test execution command

```bash
python -m pytest tests -q          # unit tests
python tests/smoke_phase6.py       # API smoke tests (server must be running)
cd frontend && npm run build       # frontend build check
```

## 15. Default administrator setup

Created automatically by `init_db`:

| Role | Email | Password |
|------|-------|----------|
| Administrator | abdulrafay.dev00@gmail.com | Password@123 |
| Customer | umer@gmail.com | Password@123 |
| Service Center | hifza@gmail.com | Password@123 |
| Reviewer | veeraj@gmail.com | Password@123 |

Change the admin password after first login in production.

## 16. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: tensorflow` | `pip install tensorflow` |
| `ModuleNotFoundError: pymysql` / DB error | Start MySQL; check `.env` credentials |
| OCR text empty | Install Tesseract; verify the path in `document_parser.py` |
| "Model not found" | Run the training commands in section 8 |
| Frontend cannot connect | Ensure backend is on port 8000 and frontend on 5174 |
| `Access denied for user 'root'` | Set `DB_PASSWORD` in `.env` |
| Port already in use | Change the port or stop the conflicting process |
