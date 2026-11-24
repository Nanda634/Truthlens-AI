# TruthLens AI — Multimodal Digital Authenticity Detection System

TruthLens AI accepts images, video, audio, PDF, and DOCX files and produces an
explainable, evidence-backed authenticity assessment: **AUTHENTIC / LIKELY_AUTHENTIC /
SUSPICIOUS / LIKELY_MANIPULATED / AI_GENERATED / LIKELY_AI_GENERATED / TAMPERED /
INCONCLUSIVE / UNSUPPORTED**, with confidence, risk score, per-signal evidence,
limitations, and a downloadable PDF forensic report.

## ⚠️ Scope of this build

This is a real, runnable full-stack implementation of the platform's architecture
and every part that does **not** require a trained deep-learning model:

- Full auth, upload, hashing, validation, database, evidence aggregation, risk
  scoring, reporting, and dashboard UI — all working end-to-end.
- **Image Forensics Engine**: real EXIF/metadata analysis, Error Level Analysis,
  noise-consistency analysis, FFT frequency analysis, ORB-based copy-move
  detection, and edge/illumination-based splicing heuristics.
- **PDF Forensics Engine**: metadata, incremental-update/EOF-marker analysis,
  embedded JavaScript detection, digital-signature presence check, and
  page-dimension consistency analysis.
- **DOCX Forensics Engine**: core properties, revision count, author/last-modified
  mismatch detection, font/formatting consistency, track-changes/comments detection.
- **Audio & Video Forensics Engines**: real container/codec metadata, frame- and
  spectral-consistency heuristics via OpenCV/librosa.

What is **intentionally not included**: trained AI-generated-image/deepfake/
synthetic-voice classifiers. No model weights ship with this project. Per the
project's own design principle, the system **never fabricates a prediction** —
every AI-classifier slot (`AIImageDetector`, video deepfake detector, audio
synthetic-voice detector) is a real, pluggable interface that returns
`"model_status": "unavailable"` and is clearly surfaced in the UI as
*"AI model unavailable — result based on forensic signals only."* until you
configure `MODEL_IMAGE_PATH` / `MODEL_VIDEO_PATH` / `MODEL_AUDIO_PATH` and
implement inference in the corresponding `ai_detector.py`.

Video/audio deepfake detection, PostgreSQL+Celery async workers, and a training
pipeline are structurally scaffolded (see `ml/` and the engine interfaces) but
require you to bring trained models and a production task queue.

## Features

- JWT authentication (register/login), per-user analysis history
- Drag-and-drop upload with SHA-256 hashing and magic-byte validation
  (never trusts file extensions)
- Real-time processing screen driven by actual backend status
- Result dashboard with risk gauge, confidence, and signal-category chart
- Evidence Explorer with per-signal severity, score, and description
- Downloadable PDF forensic report
- Analysis history with search and filters
- Responsive dark forensic-dashboard UI (desktop → mobile)

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, Axios, React Router, Recharts, Lucide Icons
**Backend:** FastAPI, Uvicorn, Pydantic, SQLAlchemy
**AI/Forensics:** OpenCV, NumPy, SciPy, Pillow, librosa
**Documents:** PyMuPDF, python-docx, pdfplumber, python-magic
**Database:** SQLite (dev default) / PostgreSQL (production-ready)
**Reports:** ReportLab (PDF generation)

## Project Structure

```
truthlens-ai/
  frontend/       React + Vite + Tailwind SPA
  backend/        FastAPI app (api, engines, services, models, database)
  ml/             Placeholders for training pipeline / model registry
  tests/          pytest backend tests
  docker/         Dockerfiles
  docker-compose.yml
  .env.example
```

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # edit as needed
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Interactive API docs: `http://localhost:8000/docs`
(ReDoc at `/redoc`). Uses SQLite by default — no database setup required.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

### Tests

```bash
cd truthlens-ai
pip install -r backend/requirements.txt
pytest tests/ -v
```

### Docker (full stack incl. Postgres + Redis)

```bash
docker compose up --build
```

Frontend: `http://localhost:5173` · Backend: `http://localhost:8000`

## Environment Variables

See `.env.example`. Key ones:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | `sqlite:///./truthlens.db` (dev) or `postgresql://...` (prod) |
| `JWT_SECRET` | Change this before any real deployment |
| `MAX_FILE_SIZE` | Upload size limit in bytes (default 200MB) |
| `MODEL_IMAGE_PATH` / `MODEL_VIDEO_PATH` / `MODEL_AUDIO_PATH` | Paths to trained model weights; leave blank to run in forensic-only mode |
| `WEIGHT_METADATA` / `WEIGHT_FORENSIC` / `WEIGHT_ML` / `WEIGHT_STRUCTURAL` / `WEIGHT_CONSISTENCY` | Configurable weights for the confidence model, must sum to 1.0 |

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT |
| POST | `/api/files/upload` | Upload + validate + hash a file |
| DELETE | `/api/files/{file_id}` | Delete a file |
| POST | `/api/analysis/{file_id}` | Start forensic analysis |
| GET | `/api/analysis/{analysis_id}/status` | Poll status |
| GET | `/api/analysis/{analysis_id}/result` | Get final result |
| GET | `/api/analysis/{analysis_id}/evidence` | Get full signal breakdown |
| GET | `/api/analysis/{analysis_id}/report` | Download PDF report |
| GET | `/api/analysis/history` | List past analyses |

Full interactive docs at `/docs` once the backend is running.

## Adding a Real AI Model

1. Train or obtain a classifier (e.g. a fine-tuned ConvNeXt/ViT for images).
2. Set `MODEL_IMAGE_PATH` (or `_VIDEO_`/`_AUDIO_`) in `.env`.
3. Implement the `predict()` method body in the matching `ai_detector.py`
   under `backend/app/engines/<type>/`.
4. The evidence aggregator will automatically start weighting the `ml` signal
   category once `model_status` is `"available"`.

## Security Notes

- Passwords are bcrypt-hashed, never stored in plaintext.
- Uploads are never executed; filenames are sanitized against path traversal.
- File type is verified by magic bytes, not trusted from the extension or
  declared MIME type — mismatches are flagged, not silently accepted.
- Generic exception handler prevents raw stack traces from reaching the client.
- Add a reverse proxy, rate limiting, and HTTPS termination before any
  production deployment; none of that is included here.

## Limitations

This is a development-grade MVP, not a certified forensic tool. Heuristic
signals (ELA, noise, frequency, splicing, frame-consistency, spectral-flatness)
are supporting evidence, not proof, and have not been benchmarked against a
labeled dataset. See `AGGREGATE-level` disclaimers surfaced in every API
response and PDF report:

> Automated digital-authenticity analysis can identify signals associated with
> manipulation or synthetic generation, but no automated detector can guarantee
> authenticity or manipulation in every case. Results should be independently
> verified when used for legal, financial, employment, security, journalistic,
> or other high-stakes decisions.

## Future Improvements

- Train and plug in real AI-generated-image / deepfake / synthetic-voice models
- Celery + Redis async workers for large video/audio jobs (structure is ready)
- S3-compatible object storage
- Digital-signature cryptographic verification for PDFs
- Model evaluation harness (confusion matrix, ROC-AUC, robustness to
  compression/cropping/re-encoding) under `ml/evaluation/`
