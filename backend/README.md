# WasteVisor Backend

**Know Before You Throw.** The WasteVisor API identifies household items and recommends a ranked next action, with safety guidance and explicitly labeled estimates.

This is a standalone Python backend in `backend/`. The existing root Node/React project is legacy and is not used or modified by this backend.

## Quick start

From this directory, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set runtime variables in the process environment (the app deliberately does not auto-load dotenv files), then start the API:

```powershell
$env:DEMO_MODE = "true"
$env:DB_PATH = "./wastevisor.db"
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for generated OpenAPI documentation. `backend/.env.example` lists supported variable names and sample values; AWS credentials use the normal boto3 credential chain (for example, an IAM role).

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AWS_REGION` | `us-east-1` | Region for Bedrock Converse. |
| `BEDROCK_MODEL_ID` | empty | Model identifier; empty means identify returns a safe confirmation-required fallback. |
| `DEMO_MODE` | `true` | When true, a recognized multipart `sample_id` returns its cached identification. |
| `DB_PATH` | `./wastevisor.db` | SQLite database path. |
| `DATABASE_URL` | empty | Optional SQLAlchemy URL override; when set it takes precedence over `DB_PATH`. |
| `CORS_ORIGINS` | localhost ports 3000 | Comma-separated allowed origins for a future frontend. |
| `MAX_UPLOAD_SIZE_BYTES` | 5 MiB | Maximum accepted image size. |

Settings are read from process environment only. No local `.env` file is opened by the application.

## Demo mode

Start the server with `DEMO_MODE=true`, then run:

```powershell
python scripts/demo_flow.py
```

The script uses the cached working-smartphone sample and exercises identify → recommend → complete → impact. Set `WASTEVISOR_API_URL` to use another local base URL. Cached sample choices are listed at `GET /api/demo/samples`; their images are served under `/samples/`. `DEMO_MODE=false` uses the live Bedrock path when `BEDROCK_MODEL_ID` and AWS credentials are available.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/identify` | Identify a JPEG, PNG, or WebP image (maximum 5 MiB). |
| `POST` | `/api/recommend` | Rank next actions from item and condition rules. |
| `POST` | `/api/actions/complete` | Store an eligible completed action and return updated estimates. |
| `GET` | `/api/history` | List completed actions with pagination. |
| `GET` | `/api/impact` | Aggregate labeled estimates from completed SQLite records. |
| `GET` | `/api/items` | List the 14 supported items and conditions. |
| `GET` | `/api/health` | Report service, demo, model-configuration, and storage status. |
| `GET` | `/api/demo/samples` | List cached demo scenarios. |

See [`../docs/api.md`](../docs/api.md) for complete schemas and examples. Errors use `{"error":{"code":"...","message":"..."}}`.

## Development checks

Run from `backend/`:

```powershell
ruff check .
mypy app
pytest
```

The optional live Bedrock test is marked `live` and skipped by default. Enable it with `RUN_LIVE_TESTS=1`, `BEDROCK_MODEL_ID`, and AWS credentials in the boto3 credential chain, then run `pytest -m live`.

## Limitations

- The API is a hackathon prototype with no authentication or multi-user isolation; history is local to one SQLite database.
- Vision confidence and item identification depend on the configured model. If it is unavailable or output is malformed, WasteVisor safely asks the user to confirm instead of pretending to identify the item.
- The 14-item knowledge base is intentionally narrow. Unknown items receive general caution guidance and no fabricated impact figures.
- Value and environmental figures are prototype estimates with assumptions documented in `app/data/impact_factors.yaml`. Reuse/resale CO₂e estimates represent possible avoided replacement manufacturing, not mass converted to emissions; factors are not action-specific measurements or verified lifecycle assessments.
- Local recycling, take-back, resale, and donation availability is not verified by city. Users should confirm local acceptance; no phone numbers or business listings are supplied.
- `GET /api/health` reports whether a model ID is configured, not whether Bedrock credentials or network access have been live-verified.
