# WasteVisor Backend Plan — 24 Hours

**Current phase:** Slices 1–7 complete.  
**Constraint:** Python 3.11+ / FastAPI / Pydantic v2 in fresh `backend/`; existing Node/React files stay untouched.  
**Demo goal:** smartphone identify → recommend → complete → updated estimated impact.

## Slice checklist

### Slice 1 — Scaffold and contract foundation

- [x] Track product docs and add Python virtual environment, `requirements.txt`, FastAPI metadata, settings, typed error envelope, localhost CORS, and `/api/health`.
- [x] Add OpenAPI and error-envelope smoke tests.

### Slice 2 — Knowledge and factors

- [x] Add 14 supported catalog items, condition-specific action rules, priorities, and reason codes.
- [x] Validate YAML with Pydantic at startup; verify factor rows cover all catalog entries and document assumptions.

### Slice 3 — Ranking and impact

- [x] Implement deterministic ranking, safety overrides, template explanations, safe unknown-item guidance, and estimate calculators.
- [x] Test expected top action for every supported item × condition pair.

### Slice 4 — Vision provider

- [x] Add Bedrock Converse interface, strict JSON schema validation, one retry, and safe low-confidence fallback.
- [x] Mock model calls in unit tests; add optional live test skipped by default.

### Slice 5 — API and history (in progress)

- [x] Implement `/api/identify`, `/api/recommend`, `/api/items`, `/api/actions/complete`, `/api/history`, and `/api/impact` per `docs/api.md`.
- [x] Enforce JPEG/PNG/WebP allowlist and 5 MiB upload bound; persist completions in SQLite.
- [x] Aggregate impact totals from stored records and mark all values as estimates.
- [x] Run local curl demo for identify and recommend; inspect output before proceeding.

### Slice 6 — Deterministic demo path

- [x] Add cached smartphone, food-scrap, and used-battery responses plus sample images.
- [x] Add `/api/demo/samples` and readable `scripts/demo_flow.py` for identify → recommend → complete → impact.

### Slice 7 — README and final verification

- [x] Add backend README with quick setup, environment variables, demo instructions, endpoint table, and limitations.
- [x] Run pytest, Ruff, mypy, and demo script; sync docs to actual behavior.

## Cut-list if schedule slips

1. Keep SQLite but use synchronous SQLAlchemy and a single local database file.
2. Use deterministic explanation templates; defer model-written explanation prose.
3. Keep demo to smartphone, food scraps, and used battery; other catalog entries retain safe rules.
4. Defer authentication, location lookup, external marketplace/service integrations, deployment, and background jobs.
5. Do not cut hazard handling, estimate provenance/labels, accurate OpenAPI schemas, or offline demo reliability.
