# WasteVisor Backend Plan — 24 Hours

**Current phase:** Phase 0 only. Inspect and document; stop for review before feature code.  
**Constraint:** Python 3.11+ / FastAPI / Pydantic v2 in fresh `backend/`; existing Node/React files stay untouched.  
**Demo goal:** smartphone identify → recommend → complete → updated estimated impact.

## Phase 0 — Inspect and design (0–2 h) — current

- [x] Inspect repository, current stack, scripts, environment template, and tests.
- [x] Record existing JavaScript project as legacy context; no edits to it.
- [x] Specify the API contract and concise architecture/decision docs.
- [x] Review Phase 0 documents and confirm scope before implementation.

## Proposed implementation slices

### Slice 1 — Backend skeleton, schemas, API contract (2–5 h)

- [x] Create `backend/`, Python virtual environment, `requirements.txt`, FastAPI app, settings, typed error envelope, localhost CORS.
- [ ] Implement Pydantic v2 request/response models and `/api/health`, `/api/items`, `/api/demo/samples`.
- [x] Verify generated `/docs` against `docs/api.md`; add API/schema tests.

### Slice 2 — Knowledge base, ranking, impact factors (5–10 h)

- [ ] Add 12–15 supported item definitions and condition-specific eligible actions in validated YAML/JSON.
- [ ] Add documented impact/value factors; all outputs labeled `is_estimate: true`.
- [ ] Implement deterministic ranking, hazard overrides, unknown-item safe fallback, and matrix tests for every item/condition.

### Slice 3 — Identification and recommendations (10–15 h)

- [ ] Implement `/api/identify` with image validation, strict Pydantic output validation, one retry, and safe low-confidence behavior.
- [ ] Wrap vision provider behind `services/vision.py`; mock provider in tests.
- [ ] Implement `/api/recommend`; LLM may phrase action explanations only, with a template fallback.

### Slice 4 — Completion, history, impact (15–19 h)

- [ ] Persist completed actions in SQLite (or JSON if needed to protect schedule).
- [ ] Implement `/api/actions/complete`, `/api/history`, and `/api/impact` with estimate labels.
- [ ] Verify smartphone hero flow updates estimated totals.

### Slice 5 — Demo mode, verification, handoff (19–24 h)

- [ ] Add `DEMO_MODE`, cached sample JSON and 3–4 sample images for smartphone, food scraps, and used battery.
- [ ] Add readable `scripts/demo_flow.py` for identify → recommend → complete → impact.
- [ ] Run pytest, Ruff, type checker, and script; fix failures and document limitations.
- [ ] Write backend README with setup, env vars, demo mode, endpoint table, and limitations.

## Cut-list (if schedule slips)

1. Replace SQLite with a local JSON store, retaining the same API contract and tests.
2. Skip LLM-generated explanations; use deterministic templates (ranking remains rules-based).
3. Reduce to three polished hero scenarios (working/dead smartphone, food scraps, used battery) while keeping other supported catalog items safe and explicit.
4. Defer location-specific service lookup, accounts, authentication, background jobs, and deployment infrastructure.
5. Do not cut hazard handling, estimate provenance/labels, API schema accuracy, or the recorded demo's deterministic path.
