# 🗑️ WasteVisor

**"Know Before You Throw."**

WasteVisor is a household waste management advisor API that identifies waste items from photos and recommends the best next action — reuse, recycle, donate, compost, or safely dispose. It follows a guided journey: **SEE → IDENTIFY → UNDERSTAND → CHOOSE ACTION → MANAGE → TRACK**.

> Built with **Python 3.11+**, **FastAPI**, and **Amazon Bedrock** for vision — with deterministic, rules-based action ranking.

---

## ✨ Features

- 📷 **Image Identification** — Upload a photo and get a structured identification of the waste item via Amazon Bedrock (Nova) vision model.
- 📋 **Deterministic Action Ranking** — Rules-based ranking (no LLM choosing actions) with 10 action types across 14 item categories and 4 condition levels.
- ⚠️ **Hazard Safety Overrides** — Swollen batteries, mercury, leaking chemicals — hazard flags override normal ranking and surface safe handling instructions first.
- 📊 **Impact Tracking** — Track completed actions and view aggregated environmental impact: waste diverted (kg), CO₂e saved, and estimated value recovered (₹).
- 🎯 **Demo Mode** — Three built-in sample scenarios (smartphone, food scraps, used battery) with cached responses for deterministic demos.
- 🔒 **Safety-First Design** — Unknown or low-confidence items require user confirmation. No fabricated listings, phone numbers, regulations, or prices.

---

## 🏗️ Architecture

```
backend/app/
├── main.py              # FastAPI app factory, CORS, lifespan, error handlers
├── core/config.py       # Pydantic Settings (env-only)
├── api/                 # Route handlers
│   ├── health.py        #   GET  /api/health
│   ├── identify.py      #   POST /api/identify
│   ├── recommend.py     #   POST /api/recommend
│   ├── items.py         #   GET  /api/items
│   ├── tracking.py      #   POST /api/actions/complete
│   │                    #   GET  /api/history
│   │                    #   GET  /api/impact
│   └── demo.py          #   GET  /api/demo/samples
├── schemas/             # Pydantic v2 request/response models
├── services/
│   ├── vision.py        #   Bedrock Converse (image → identification)
│   ├── ranking.py       #   Deterministic rules-based action ranking
│   ├── impact.py        #   Impact & value estimation from factor table
│   └── history.py       #   SQLite persistence (SQLAlchemy)
└── data/
    ├── loader.py         #   YAML loader + startup validation
    ├── knowledge_base.yaml  # 14 items, conditions, rule sets
    └── impact_factors.yaml  # Per-item impact/value factors
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) AWS credentials for Bedrock vision — without them, the app runs in safe-fallback / demo mode.

### Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

### Configure

Copy the example env file and adjust as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `true` | Use cached demo responses |
| `AWS_REGION` | `us-east-1` | Bedrock region |
| `BEDROCK_MODEL_ID` | _(empty)_ | Vision model ID; empty = safe fallback |
| `DB_PATH` | `./wastevisor.db` | SQLite database path |
| `CORS_ORIGINS` | `localhost:3000` | Allowed CORS origins |
| `MAX_UPLOAD_SIZE_BYTES` | `5242880` | Max upload size (5 MB) |

### Run

```bash
uvicorn app.main:app --reload
```

API docs available at **http://localhost:8000/docs** (Swagger UI) and **http://localhost:8000/redoc**.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health, config, and storage info |
| `POST` | `/api/identify` | Upload an image (JPEG/PNG/WebP, ≤5 MB) → item identification |
| `POST` | `/api/recommend` | Get ranked action recommendations for a confirmed item + condition |
| `GET` | `/api/items` | List all 14 supported catalog items with conditions and hazard info |
| `POST` | `/api/actions/complete` | Record a completed action and get updated impact totals |
| `GET` | `/api/history` | Paginated history of completed actions (`limit`, `offset`) |
| `GET` | `/api/impact` | Aggregated impact totals (waste diverted, CO₂e saved, value recovered) |
| `GET` | `/api/demo/samples` | List 3 demo sample scenarios with image URLs |

All errors follow a single envelope: `{"error": {"code": "...", "message": "..."}}`.

For full request/response schemas, see the interactive docs at `/docs` or the [API documentation](docs/api.md).

---

## 🧪 Testing & Quality

```bash
cd backend

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy app
```

### Test Coverage

| Test File | Scope | Tests |
|---|---|---|
| `test_health.py` | Health endpoint, OpenAPI branding, error envelope, startup validation | 4 |
| `test_ranking.py` | All item×condition pairs, hazard overrides, unknown fallback, estimate labels | 56+ |
| `test_vision.py` | Bedrock mocking, retries, fallbacks, low-confidence, live marker | 6 |
| `test_api.py` | Full integration: identify, recommend, complete, history, impact, items, demo | 7 |

---

## 📦 Supported Items

WasteVisor's knowledge base covers **14 household items** across these categories:

| Category | Items |
|---|---|
| **Electronics** | Old Smartphone, Computer Accessories, Small Appliance |
| **Hazardous** | Household Battery, Household Bulb, Cooking Oil, Medicine Strips |
| **Recyclables** | PET Bottle, Glass Bottle, Cardboard Box, Paper |
| **Reusables** | Clothing, Furniture |
| **Organic** | Food Scraps |

Each item is evaluated across **4 conditions**: `working`, `damaged`, `dead`, `unknown`.

### Action Types

`reuse` · `resale` · `repair` · `donate_refurbish` · `compost` · `recycling` · `authorized_disposal` · `hazardous_collection` · `used_cooking_oil_collection` · `medicine_takeback`

---

## 🔐 Design Principles

- **Deterministic ranking** — Action ranking is rules-based and independent of LLM prose generation.
- **Hazard safety first** — Hazard flags override the normal action hierarchy with safe handling guidance.
- **No fabricated data** — The system never invents local listings, phone numbers, regulations, or ₹ values. All estimates are labeled with their basis and source.
- **Unknown item safety** — Low-confidence or unrecognized items require user confirmation before any action is recommended.
- **Provider isolation** — Vision provider details (Bedrock, model IDs, errors) are never exposed in API responses.

---

## 📄 License

This project is for educational and demonstration purposes.

