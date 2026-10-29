# WasteVisor — Project Context

> **Know Before You Throw.**

WasteVisor is a household waste-management advisor. It answers **“What should I do with this waste?”** with ranked, explainable next actions; it is not merely a classifier.

Product flow: **SEE → IDENTIFY → UNDERSTAND → CHOOSE ACTION → MANAGE → TRACK**.

## Current phase and stack

The current phase is **backend only**. Define and implement a stable API for a future frontend. Do not build UI, pages, components, styling, or frontend interactions.

The backend stack is locked to Python 3.11+, FastAPI, Uvicorn, and Pydantic v2. Use `requirements.txt`, a Python virtual environment, SQLite (SQLAlchemy/SQLModel) or JSON if simpler, pytest, Ruff, and mypy or Pyright. The existing JavaScript repository is legacy context only: do not build on it, add JS tooling, or delete/modify its files. Create the new backend under `backend/`.

## Inspected repository state (2026-10-29)

- Existing root project is Node.js/Express with React 18/Vite, Jest, and Amazon Bedrock Runtime SDK. It has `server.js`, `src/visionProvider.js`, `src/ruleEngine.js`, `src/waste_rules.json`, `src/App.jsx`, and `tests/visionProvider.test.js`.
- Existing API is only `POST /api/analyze` (multipart image, classification plus action strings). It is not the target contract and must remain untouched.
- Bedrock is called from JavaScript; the local fallback returns unknown with zero confidence and is rejected by its validator.
- `.env.example` contains AWS/Bedrock settings. A local `.env` exists; never read, print, or commit its secrets.
- `node_modules` exists. Existing npm scripts: `dev`, `build`, `test`, `serve`, `start`. No Python backend, SQLite history, demo samples, README, Ruff, or mypy setup is present.
- Existing frontend files are out of scope. Root `.gitignore` currently ignores `docs/`, `PLAN.md`, `PROJECT_CONTEXT.md`, and `AGENTS.md`; preserve current ignore settings unless explicitly changed in a later approved phase.

## Product rules

- Deterministic knowledge-base rules rank eligible actions by item and condition; an LLM may phrase explanations but cannot choose actions or invent figures.
- Hazardous handling overrides ordinary reuse/recycling. Used batteries must never be advised into household waste.
- Unknown or low-confidence items return safe general guidance and `needs_confirmation: true`.
- India context uses ₹ and location-dependent guidance. Do not invent phone numbers, listings, or locally verified rules.
- Impact and monetary figures come from documented factors and are always labeled estimates.

## Naming

Use **WasteVisor** consistently in code, API metadata, docs, README, and demo materials. Tagline: **“Know Before You Throw.”** Do not use alternate product names.
