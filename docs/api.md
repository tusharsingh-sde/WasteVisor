# WasteVisor API Contract (Design)

**Status:** Phase 0 proposal; implementation must generate matching FastAPI/Pydantic v2 OpenAPI schemas. Base path `/api`. JSON uses `snake_case`. The future frontend can use `/docs` for the live OpenAPI document.

## Shared conventions

- Success responses are typed JSON objects. `POST /api/identify` accepts `multipart/form-data` with field `image` and optional `sample_id` for deterministic demo selection.
- Conditions: `working | damaged | dead | unknown`.
- Every impact/value number is an estimate. Impact objects include `is_estimate: true` and a factor/source note.
- All error responses use `{"error":{"code":"...","message":"..."}}`.

Example error:

```json
{"error":{"code":"invalid_image","message":"Upload a supported image file."}}
```

Typical statuses: `400` malformed request, `413` image too large, `422` request validation, `404` unknown record/sample, `500` unexpected server error, `503` unavailable required provider. Do not expose stack traces, credentials, or provider internals.

## `POST /api/identify`

Identify the uploaded item and return a strict structured result. In demo mode, a supplied known `sample_id` uses the cached sample. Live mode calls the configured vision provider; malformed output is retried once and then degrades safely.

**Request:** `multipart/form-data`

- `image` (required): supported image upload.
- `sample_id` (optional): sample identifier listed by `/api/demo/samples`; honored for cached result selection when demo mode is enabled.

**Response `200`:**

```json
{
  "identification": {
    "item": "old_smartphone",
    "display_name": "Old smartphone",
    "material": ["glass", "aluminum", "lithium_ion_battery"],
    "category": "e_waste",
    "condition": "working",
    "hazard_flags": ["contains_battery"],
    "confidence": 0.91,
    "needs_confirmation": false
  },
  "demo": {"is_demo": true, "sample_id": "smartphone_working"}
}
```

For uncertain items, set confidence low, condition `unknown` as needed, and `needs_confirmation: true`; include safe general guidance in an optional `safe_guidance` string. The client must allow confirmation/edit before recommending.

## `POST /api/recommend`

Return deterministic, rules-ranked actions for a user-confirmed identification. The language model may phrase `why_best` but cannot select or reorder actions.

**Request JSON:**

```json
{
  "item": "old_smartphone",
  "condition": "working",
  "city": "Pune",
  "context": {"has_original_box": true, "user_goal": "sell"}
}
```

`city` and `context` are optional. Item and condition are required; unsupported items return a safe fallback and confirmation indicator, not guessed local instructions.

**Response `200`:**

```json
{
  "item": "old_smartphone",
  "condition": "working",
  "needs_confirmation": false,
  "recommended_actions": [
    {
      "action_type": "resale",
      "rank": 1,
      "why_best": "A working phone can stay in use and may recover value.",
      "reason_codes": ["WORKING_ELECTRONIC", "VALUE_RECOVERY"],
      "effort_minutes": 30,
      "estimated_value_inr": {
        "min": 1000,
        "max": 8000,
        "is_estimate": true,
        "basis": "Illustrative range from documented factor table; actual resale depends on model and condition."
      },
      "impact": {
        "kg_diverted": 0.18,
        "co2e_saved_kg": 35.0,
        "is_estimate": true,
        "basis": "Factor assumptions documented in data/impact_factors.yaml."
      },
      "next_steps": ["Back up and erase personal data.", "Check battery and screen condition.", "Compare a few resale offers."],
      "preparation_checklist": ["Factory reset", "Remove SIM and memory card", "Include charger if available"],
      "safety_warning": "Do not sell a swollen or damaged lithium-ion battery device; seek authorized e-waste handling."
    }
  ]
}
```

Impact and value fields are estimates and may be `null` when the factor table has no defensible value. Safety warnings may be `null` when none is required.

## `POST /api/actions/complete`

Record that a recommended action was completed and return updated estimated totals.

**Request JSON:**

```json
{
  "item": "old_smartphone",
  "condition": "working",
  "action_type": "resale",
  "completed_at": "2026-10-29T12:00:00Z",
  "recovered_value_inr": 3500
}
```

`completed_at` and `recovered_value_inr` are optional; server timestamp is used when omitted. Do not accept a client-supplied impact value as authoritative; calculate from server factors.

**Response `201`:**

```json
{
  "history_entry": {
    "id": "act_01JXYZ",
    "item": "old_smartphone",
    "condition": "working",
    "action_type": "resale",
    "completed_at": "2026-10-29T12:00:00Z",
    "impact": {"kg_diverted": 0.18, "co2e_saved_kg": 35.0, "is_estimate": true},
    "recovered_value_inr": {"value": 3500, "is_estimate": true}
  },
  "totals": {
    "kg_diverted": {"value": 0.18, "is_estimate": true},
    "co2e_saved_kg": {"value": 35.0, "is_estimate": true},
    "recovered_value_inr": {"value": 3500, "is_estimate": true}
  }
}
```

## `GET /api/history`

Return recorded completed actions (prototype is single-user/local; no authentication).

**Query:** optional `limit` (default 50, bounded) and `offset` (default 0).

**Response `200`:**

```json
{
  "items": [
    {"id":"act_01JXYZ","item":"old_smartphone","condition":"working","action_type":"resale","completed_at":"2026-10-29T12:00:00Z","impact":{"kg_diverted":0.18,"co2e_saved_kg":35.0,"is_estimate":true},"recovered_value_inr":{"value":3500,"is_estimate":true}}
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

## `GET /api/impact`

Return running totals derived from completed history and documented factors.

**Response `200`:**

```json
{
  "kg_diverted": {"value": 0.18, "is_estimate": true},
  "co2e_saved_kg": {"value": 35.0, "is_estimate": true},
  "recovered_value_inr": {"value": 3500, "is_estimate": true},
  "basis": "Totals are estimates calculated from documented WasteVisor factors and completed actions."
}
```

## `GET /api/items`

Return the supported catalog and allowable conditions so a frontend can render confirmation/edit controls.

**Response `200`:**

```json
{
  "items": [
    {"id":"old_smartphone","display_name":"Old smartphone","category":"e_waste","conditions":["working","damaged","dead","unknown"],"hazard_flags":["contains_battery","swollen_battery"]},
    {"id":"food_scraps","display_name":"Food scraps","category":"organic","conditions":["working","damaged","dead","unknown"],"hazard_flags":[]}
  ]
}
```

The initial catalog is limited to the 12–15 documented target items. `conditions` are the valid condition values; item-specific restrictions may narrow them in the data.

## `GET /api/health`

Report service readiness and model/demo configuration without leaking secrets.

**Response `200`:**

```json
{
  "status": "ok",
  "demo_mode": true,
  "model_available": false,
  "storage": "sqlite"
}
```

`model_available` is a boolean readiness indication, not provider credentials or endpoint details.

## `GET /api/demo/samples`

List sample choices available to the future frontend. This route is available regardless of `DEMO_MODE`; cached results are used only when demo mode is enabled.

**Response `200`:**

```json
{
  "samples": [
    {"id":"smartphone_working","item":"old_smartphone","label":"Working old smartphone","image_url":"/samples/smartphone_working.jpg"},
    {"id":"food_scraps","item":"food_scraps","label":"Food scraps","image_url":"/samples/food_scraps.jpg"},
    {"id":"used_battery","item":"battery_li_ion","label":"Used lithium-ion battery","image_url":"/samples/used_battery.jpg"}
  ]
}
```

Sample images and cache files are local demo assets; they do not represent real user submissions.
