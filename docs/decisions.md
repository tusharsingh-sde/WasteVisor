# WasteVisor Architecture Decisions

Decision records for the backend-only hackathon phase. Implementation has not started.

## ADR-001 — Build the new backend in Python under `backend/`

- **Status:** Accepted; required by project scope.
- **Decision:** Use Python 3.11+, FastAPI, Uvicorn, Pydantic v2, and `requirements.txt`. Create a fresh `backend/` directory. Do not build on or delete/modify the existing JavaScript project.
- **Alternatives:** Extend the current Express API; replace the root application; create a Python service elsewhere.
- **Why:** The requested Python stack is locked, while isolating it preserves the current checkout and keeps this phase backend-only.
- **Trade-off:** Two stacks will coexist in the repository. The Python API is authoritative for the future frontend; legacy JS remains untouched until separately reviewed.

## ADR-002 — Use typed HTTP contracts and generated OpenAPI

- **Status:** Proposed for implementation.
- **Decision:** Define all API request, response, and error shapes with Pydantic v2 and FastAPI; keep `/docs` consistent with `docs/api.md`.
- **Alternatives:** Untyped JSON dictionaries; hand-maintained OpenAPI only.
- **Why:** A future frontend depends on a predictable contract and can use the generated API documentation.

## ADR-003 — Rules determine eligible actions and ranking

- **Status:** Implemented in Slices 2–3.
- **Decision:** Load a small validated YAML/JSON item-condition knowledge base and rank eligible actions deterministically. A vision/LLM provider identifies the item; an LLM may phrase explanations only, with template fallback.
- **Alternatives:** Ask the LLM to directly choose the best action; train a custom ranking model.
- **Why:** Rules are auditable, testable for every supported item/condition, and safer for hazardous waste within a 24-hour build.
- **Safety note:** Condition changes ranking. A working phone can prioritize resale; a dead phone goes to authorized e-waste; a used battery requires hazardous drop-off guidance, never household bin disposal.

## ADR-004 — Put model calls behind a provider interface

- **Status:** Implemented in Slice 4; API integration is in Slice 5.
- **Decision:** Keep vision integration in `app/services/vision.py` behind a small interface, using an official Python SDK or `httpx`.
- **Alternatives:** Couple routes directly to one provider; use the existing JavaScript Bedrock module.
- **Why:** The provider can be replaced or mocked in tests without changing the API. Existing JavaScript model code is explicitly out of scope.
- **Implementation:** Uses boto3 Bedrock Converse with a strict JSON identification prompt, catalog IDs, Pydantic validation, one retry, and a confirmation-required low-confidence fallback. Provider error details are never returned to clients.

## ADR-005 — Start with local persistence

- **Status:** Implemented in Slice 5 using SQLite.
- **Decision:** Store completed actions locally and derive history and impact totals from those records. No auth or distributed database.
- **Alternatives:** MongoDB/cloud database; no persistence.
- **Why:** The hero flow requires completion to update totals, while local storage avoids infrastructure setup.
- **Trade-off:** Prototype history is single-instance/single-user and not a production multi-user data store.
- **Implementation:** Impact totals are derived by aggregating stored completed-action rows; client-supplied impact values are not accepted.

## ADR-006 — Make demo mode deterministic

- **Status:** Implemented in Slice 6.
- **Decision:** `DEMO_MODE=true` serves cached results for smartphone, food scraps, and used battery samples; ship three local sample images and `/api/demo/samples`.
- **Alternatives:** Depend on live model/network for recording; mock every request invisibly.
- **Why:** The recorded demo must work offline and repeat reliably while retaining a live path when demo mode is disabled.
- **Trade-off:** Demo results are curated fixtures and must be visibly identifiable as sample output.

## ADR-007 — Document and label estimates

- **Status:** Implemented in Slices 2–3 and 6.
- **Decision:** Keep value/impact factors in a documented table with source or assumption per row. Return figures with `is_estimate: true`; use null rather than unsupported precision.
- **Alternatives:** Hard-code plausible-looking constants in ranking code; omit provenance.
- **Why:** Prevents estimates from being mistaken for measured facts and makes assumptions auditable.
- **CO₂e assumption:** `kg_diverted` estimates the mass kept out of mixed disposal. For reuse/resale of durable goods, `co2e_saved_kg` estimates possible avoided new-item manufacturing; it is not calculated by multiplying the item's mass. Material recovery and compost rows use separate illustrative processing assumptions, and medicine has no carbon credit. These estimates are not measured lifecycle results or action-specific measurements.
- **Implementation note:** Both `method_note` and each item row's `source_note` in `backend/app/data/impact_factors.yaml` repeat this distinction so the assumption travels with returned estimates.

## ADR-008 — Keep the initial API narrow

- **Status:** Implemented in Slices 1–6; contract is documented in `docs/api.md`.
- **Decision:** Expose identify, recommend, action completion, history, impact, item catalog, health, and demo sample listing endpoints with one error envelope.
- **Alternatives:** General-purpose waste marketplace, user accounts, provider integrations, or location search.
- **Why:** These endpoints support the requested identify → recommend → complete → impact demo without heavy infrastructure.

## Scope cuts for the 24-hour limit

- Defer authentication, multi-user tenancy, external marketplace/service integrations, location search, deployment automation, and background processing.
- If time is tight, use JSON persistence and template explanations; retain safety rules, confidence handling, estimate provenance, typed API docs, and demo determinism.
