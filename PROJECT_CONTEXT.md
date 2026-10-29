# WasteVisor — Project Context

> **Know Before You Throw.**

WasteVisor is a household waste-management advisor. It answers **“What should I do with this waste?”** with ranked, explainable next actions; it is not merely a classifier.

Product flow: **SEE → IDENTIFY → UNDERSTAND → CHOOSE ACTION → MANAGE → TRACK**.

## Implemented backend

The approved scope is **backend only**. The implemented API is intended for a future frontend; do not add UI, pages, components, styling, or frontend interactions in backend work.

The backend uses Python 3.11+, FastAPI, Uvicorn, Pydantic v2, boto3 Converse, validated YAML, SQLAlchemy/SQLite, pytest, Ruff, and mypy. It lives in `backend/`. The existing JavaScript repository is legacy context only; backend work must not build on, modify, or delete it.

## Inspected repository state (2026-10-29)

- Existing root project is Node.js/Express with React 18/Vite, Jest, and Amazon Bedrock Runtime SDK. It has `server.js`, `src/visionProvider.js`, `src/ruleEngine.js`, `src/waste_rules.json`, `src/App.jsx`, and `tests/visionProvider.test.js`.
- Existing API is only `POST /api/analyze` (multipart image, classification plus action strings). It is not the target contract and must remain untouched.
- Bedrock is called from JavaScript; the local fallback returns unknown with zero confidence and is rejected by its validator.
- Backend endpoints cover identify, recommend, completion, history, impact, supported items, health, and cached demo samples. Three small local sample images power the offline demo path.
- `backend/.env.example` lists process environment settings. The app does not auto-load dotenv files; never inspect or commit local `.env` secrets.
- Root npm scripts and frontend files remain in the repository but are not part of the Python service.
- Requested project docs are now tracked; `backend/.venv`, caches, and local databases are ignored.

## Product rules

- Deterministic knowledge-base rules rank eligible actions by item and condition; an LLM may phrase explanations but cannot choose actions or invent figures.
- Hazardous handling overrides ordinary reuse/recycling. Used batteries must never be advised into household waste.
- Unknown or low-confidence items return safe general guidance and `needs_confirmation: true`.
- India context uses ₹ and location-dependent guidance. Do not invent phone numbers, listings, or locally verified rules.
- Impact and monetary figures come from documented factors and are always labeled estimates. Durable-goods reuse/resale CO₂e represents possible avoided new-item manufacturing, not item mass converted to emissions.

## Naming

Use **WasteVisor** consistently in code, API metadata, docs, README, and demo materials. Tagline: **“Know Before You Throw.”** Do not use alternate product names.
