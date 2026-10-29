# WasteVisor Contributor Instructions

## Scope and stack

- **Backend only, no UI work.** Do not create or modify frontend pages, components, styling, or interactions.
- Implement new backend work in `backend/`; leave the existing Node.js/React files untouched and do not delete them.
- Use Python 3.11+, FastAPI, Uvicorn, Pydantic v2, `requirements.txt`, pytest, Ruff, and mypy or Pyright. Use SQLite via SQLAlchemy/SQLModel, or JSON when a simpler prototype store is sufficient.
- Keep API schemas typed and OpenAPI `/docs` accurate. Enable localhost CORS for the future frontend.

## Product and naming

- WasteVisor advises on the best next action; it is not just a classifier.
- Keep the journey **SEE → IDENTIFY → UNDERSTAND → CHOOSE ACTION → MANAGE → TRACK**.
- Use the name **WasteVisor** consistently in code, API metadata, docs, README, and comments. Tagline: **“Know Before You Throw.”** Do not introduce alternate product names.
- Rank actions from the local knowledge base by item and condition. Hazard safety overrides the ordinary hierarchy. Unknown or low-confidence items require confirmation and safe guidance.
- Do not invent local listings, phone numbers, regulations, environmental figures, or ₹ values. Explain assumptions and label estimates.

## Commands (from `backend/`)

- Create environment: `python -m venv .venv`
- Activate on Windows: `.venv\\Scripts\\Activate.ps1`; on macOS/Linux: `source .venv/bin/activate`
- Install: `python -m pip install -r requirements.txt`
- Run API: `uvicorn app.main:app --reload`
- Test: `pytest`
- Lint: `ruff check .`
- Type check: `mypy app` (or the documented Pyright equivalent)

## Engineering conventions

- Keep provider calls behind `app/services/vision.py`; keep ranking deterministic and independent of LLM prose generation.
- Load and validate YAML/JSON knowledge-base and impact factors at startup.
- Use one error envelope: `{"error":{"code":"...","message":"..."}}`. Do not leak stack traces or secrets.
- Read configuration from environment variables; provide `.env.example`, never commit `.env` or credentials.
- Keep demo mode deterministic and make sample results clearly identifiable.
- Make focused vertical slices and update `PLAN.md` checkboxes and `docs/decisions.md` when scope changes.

## Definition of done

- Relevant pytest tests pass; Ruff and the selected type checker pass.
- OpenAPI request/response schemas match `docs/api.md`.
- Safety overrides, unknown-item confirmation, and estimate labels are covered.
- Demo path is deterministic; errors are logged without exposing internals.
- No UI/frontend work or changes to the existing JavaScript project are included.
