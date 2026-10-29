# Product & Architecture Review

**Reviewer role:** Senior Product Architect & Technical Lead
**Date:** 2026‑10‑09
**Status:** Pre‑implementation gate review

---

## 1. PRODUCT THESIS

### Assessment: STRONG — with one critical fix needed

The core differentiation is clear:

> "Most waste‑management apps tell you *where* waste goes.
> WasteVisor tells you *what you should do with it first.*"

This is a genuinely defensible thesis for a hackathon. It reframes waste from a disposal problem into an **action‑selection** problem. That reframe is the entire product.

**However, the existing documentation weakens the thesis by burying it.** The `PROJECT_CONTEXT.md` opens with a six‑step pipeline (SEE → IDENTIFY → UNDERSTAND → CHOOSE → MANAGE → TRACK) that reads like an engineering spec, not a product pitch. A hackathon judge will spend 10 seconds reading the README. The thesis must be the *first sentence*.

### Verdict
- **Thesis is strong enough for a hackathon win** — but only if the demo and UI lead with the thesis, not the pipeline diagram.
- The six‑step flow should be treated as internal architecture, never shown to users or judges as the product summary.

---

## 2. MVP SCOPE

The existing `PLAN.md` lists far too many deliverables for a 24‑hour hackathon. Below is a ruthless triage.

### MUST HAVE (ship or fail)
| # | Feature | Why |
|---|---------|-----|
| M1 | **Image upload** (file picker + drag‑drop) | The product starts here. No upload = no product. |
| M2 | **AI‑powered identification** (real, not mock) | A mock stub means the demo is a slideshow. Judges will ask "is this real?" We need at minimum an LLM with vision (e.g., Claude, GPT‑4o, or Gemini) analyzing the image and returning structured JSON. |
| M3 | **Deterministic recommendation engine** | Rule‑based mapping from structured classification → ranked next‑actions. This is the product's soul. |
| M4 | **Result screen with ranked action cards** | The "wow" moment. Must be visually polished. |
| M5 | **One complete demo flow** (upload → result → actions) | The critical path that the 3‑minute demo will follow. |

### NICE TO HAVE (build only if M1–M5 are solid)
| # | Feature | Why deferred |
|---|---------|--------------|
| N1 | Waste Inventory / History list | Adds narrative depth ("I've processed 12 items this week") but is not the core loop. |
| N2 | WasteScore / impact summary | Impressive for demo but requires made‑up numbers unless we source real data. |
| N3 | Dark mode toggle | Cosmetic. Pick one theme and commit. |
| N4 | Camera capture (navigator.mediaDevices) | File upload is sufficient for demo. Camera adds mobile‑only complexity. |

### REMOVE FROM MVP
| # | Feature | Why cut |
|---|---------|--------|
| X1 | **Service integration links** (recycling centres, resale, donation URLs) | Hard‑coded URLs to random services add no value and look fake. Replace with a "WasteVisor would connect you to…" placeholder in the action card. |
| X2 | **Express backend** | Unnecessary layer. The front‑end can call an AI API directly (or via a thin serverless proxy). Express adds a second process to manage, a second port, CORS config, and a multipart parser — all for forwarding one request. |
| X3 | **CI scripts** | No CI pipeline needed for a 24‑hour hackathon. |
| X4 | **react-router** | The MVP is a single‑screen app. Routing adds complexity for zero benefit. |
| X5 | **Carbon‑saved estimates** | We have no credible data source. Making up numbers is worse than showing nothing. |
| X6 | **Internationalisation** | Zero users, zero locales needed for demo. |

### Critical call‑out: MOCK VISION IS NOT ACCEPTABLE

The existing plan proposes a "static JSON mapping image names to categories." This means the demo would show a pre‑mapped image returning a pre‑written result. **Any judge will see through this immediately.** It is the single most damaging decision in the current plan.

**Recommendation:** Use a multimodal LLM API (Claude with vision, GPT‑4o, or Gemini 2.0 Flash) as the vision+identification layer. Send the image, receive structured JSON. This is a single API call and takes less time to implement than building a convincing mock dataset.

---

## 3. CORE USER FLOW

### Proposed flow (from the brief):
```
Upload photo → AI identifies → structured classification → rule engine → ranked actions → user sees best action → alternatives → Waste Inventory → WasteScore
```

### Reviewed flow (recommended):
```
Upload photo
  → Multimodal LLM returns structured identification
      { item, material, condition, category, hazardous: bool, reusable: bool }
  → Deterministic rule engine ranks actions based on structured fields
  → UI renders result:
      ┌─────────────────────────────────────┐
      │  [Image thumbnail]                  │
      │  Item: Old smartphone               │
      │  Material: Mixed (metal, glass, Li) │
      │  Condition: Functional              │
      │                                     │
      │  ★ BEST ACTION: Sell or Trade‑in    │
      │    → Estimated value: ₹2,000–4,000  │
      │                                     │
      │  Other options:                     │
      │    2. Donate (if functional)         │
      │    3. Certified e‑waste recycler     │
      │                                     │
      │  ⚠ WARNING: Contains lithium‑ion    │
      │  battery. Do NOT dispose in regular  │
      │  waste.                             │
      └─────────────────────────────────────┘
  → (Optional) Save to inventory
```

### What changed:
1. **Removed WasteScore from the critical path.** It's a vanity metric with no grounding. Move it to Nice‑to‑Have.
2. **Added hazard warnings as a first‑class UI element.** Safety callouts should appear on the result screen, not buried.
3. **Made Waste Inventory optional.** The core loop is upload → result. Inventory is additive, not essential.
4. **Merged "structured classification" and "AI identification" into one LLM call.** The LLM returns the structured JSON directly — no separate "classification" step.

---

## 4. AI ARCHITECTURE

### Recommended separation of concerns:

```
Layer 1: VISION + IDENTIFICATION (LLM — trustworthy here)
  Input:  Raw image
  Output: Structured JSON
          { item, material, condition, category, hazardous, reusable, compostable }
  Trust level: MEDIUM. LLMs are good at identifying common objects.
  Mitigation: Confidence field + "Not sure? Tell us what this is" fallback.

Layer 2: DETERMINISTIC RULE ENGINE (NO LLM — code only)
  Input:  Structured JSON from Layer 1
  Output: Ranked list of actions with metadata
  Trust level: HIGH. Rules are authored by us, fully auditable.
  This is where the product logic lives.

Layer 3: EXPLANATION GENERATION (LLM — optional, constrained)
  Input:  Selected action + item context
  Output: 1–2 sentence natural‑language explanation
  Trust level: LOW if unconstrained. Must be templated or heavily prompted.
  Mitigation: Use templates with variable substitution for MVP.
              e.g., "Your {item} is in {condition} condition.
                     We recommend {action} because {reason}."
```

### Where the LLM must NOT be trusted:

| Area | Risk | Mitigation |
|------|------|------------|
| **Hazard classification** | LLM might say a lithium battery is "safe to bin" | Rule engine OVERRIDES LLM: if `material` contains battery/lithium/chemical → force hazardous pathway |
| **Resale value estimates** | LLM will hallucinate prices | Do NOT show specific prices. Use qualitative language: "This item may have resale value" |
| **Disposal regulations** | Vary by jurisdiction, LLM will guess | Show generic safe advice + "Check your local council" disclaimer |
| **Environmental impact numbers** | CO₂ savings, landfill diversion stats | Do NOT generate. Only show if sourced from a credible dataset |
| **Medical/chemical safety** | LLM might understate danger | Hard‑coded rule: if category ∈ {medical, chemical, hazardous} → show safety warning, recommend professional disposal |

---

## 5. WASTE DECISION LOGIC

### Problem with the current approach

The existing plan uses a **single universal priority list**:
```
reuse > resale > repair > donation > compost > recycle > hazardous disposal
```

**This is wrong.** You cannot rank "reuse" above "hazardous disposal" for a leaking car battery. The ranking must be **conditional on the item's properties.**

### Recommended decision matrix:

```
IF hazardous OR medical OR chemical:
    → ALWAYS: "Authorized disposal / special handling"
    → NEVER suggest reuse, resale, donation
    → Show safety warning prominently

ELSE IF electronic AND functional:
    → 1. Sell / Trade‑in
    → 2. Donate
    → 3. Certified e‑waste recycling

ELSE IF electronic AND non‑functional:
    → 1. Repair (if repairable)
    → 2. Certified e‑waste recycling
    → NEVER suggest regular bin

ELSE IF organic / food waste:
    → 1. Compost
    → 2. Municipal green bin
    → NOT resale, NOT donation

ELSE IF textile AND good condition:
    → 1. Donate
    → 2. Resell
    → 3. Textile recycling

ELSE IF textile AND poor condition:
    → 1. Textile recycling
    → 2. Repurpose (cleaning rags, etc.)

ELSE IF glass / metal / paper (recyclable commodity):
    → 1. Recycle (specify stream)
    → 2. Reuse / repurpose if applicable

ELSE IF reusable AND good condition:
    → 1. Reuse
    → 2. Donate
    → 3. Resell

ELSE (general waste):
    → 1. Check recyclability
    → 2. General waste bin
```

This is a decision **tree**, not a flat ranking. It must be implemented as branching logic, not a sorted list.

### Key rule: Hazardous items get a HARD OVERRIDE

No matter what the LLM says about condition or reusability, if the item is flagged as hazardous, the system must:
1. Show a prominent warning (red/orange, icon)
2. Recommend only authorized disposal channels
3. Never suggest reuse, donation, or resale

---

## 6. SAFETY + TRUST

### Items requiring conservative treatment:

| Item type | Danger | Required behaviour |
|-----------|--------|--------------------|
| **Lithium‑ion batteries** | Fire, explosion, toxic fumes | "Do NOT place in regular waste. Take to an authorized e‑waste collection point." Hard‑coded, never overridden by LLM. |
| **E‑waste** (phones, laptops, TVs) | Heavy metals, toxic components | "Certified e‑waste recycler required." Never suggest regular bin. |
| **Medical waste** (syringes, medication) | Biohazard, drug contamination | "Contact your local pharmacy or medical waste service." Never suggest donation or reuse. |
| **Chemicals** (paint, solvents, cleaners) | Toxic, flammable | "Take to a hazardous waste collection event." Show safety icon. |
| **Broken glass** | Laceration risk | "Wrap securely before disposal. Do not place loose in recycling." |
| **Asbestos‑containing materials** | Carcinogenic | "Do NOT handle. Contact a licensed asbestos removal service." |

### Claims that require disclaimers:

| Claim type | Required wording |
|------------|------------------|
| Resale value | "May have resale value" — never a specific price |
| Environmental impact | "Estimated" or omit entirely if unsourced |
| Recyclability | "Check your local recycling guidelines" — rules vary by municipality |
| Compostability | "Suitable for home composting" vs. "Requires industrial composting" — distinguish clearly |
| Disposal legality | "Regulations vary by location. Check with your local council." |

### Global safety disclaimer (must appear in the app):
> "WasteVisor provides general guidance only. Always follow your local waste disposal regulations. For hazardous materials, contact your local authority."

---

## 7. DEMO STRATEGY

### Available demo items:
| Item | Showcase value | Verdict |
|------|---------------|---------|
| A. Old smartphone | HIGH — shows electronics path, resale suggestion, e‑waste warning, multi‑action result | **USE — lead with this** |
| B. Banana peel | MEDIUM — simple, shows organic/compost path, fast | **USE — show speed + contrast** |
| C. Newspaper | LOW — boring, obvious answer ("recycle"), no drama | **SKIP** |
| D. Glass bottles | MEDIUM — shows recyclable path, but not exciting | **SKIP** |
| E. Household waste inventory | HIGH — but only if N1 is built | **USE only if time permits** |

### Recommended 3‑minute demo script:

```
[0:00–0:30]  PROBLEM STATEMENT
  "Every day, millions of usable items end up in landfills
   because people don't know the best option.
   WasteVisor changes that."
  Show tagline: "Know Before You Throw."

[0:30–1:15]  DEMO 1 — Old Smartphone (the hero moment)
  Upload photo of old smartphone.
  WasteVisor identifies: "Smartphone — Mixed materials — Functional"
  Recommendation: ★ Sell or Trade‑in
  Alternatives: Donate, Certified e‑waste recycling
  ⚠ "Contains lithium‑ion battery — never dispose in regular waste"
  → This single demo shows: real AI identification, smart ranking,
     safety awareness, and actionable advice.

[1:15–1:45]  DEMO 2 — Banana Peel (speed + contrast)
  Upload photo of banana peel.
  WasteVisor identifies: "Banana peel — Organic — Compostable"
  Recommendation: ★ Home compost
  Alternative: Municipal green bin
  → Shows that WasteVisor handles trivial items instantly too.
    The contrast with the smartphone proves the system is adaptive,
    not one‑size‑fits‑all.

[1:45–2:15]  WASTE INVENTORY (if built, else extend problem statement)
  Show the inventory: "You've processed 2 items today."
  Brief flash of the history view.
  → Demonstrates tracking without lingering.

[2:15–2:45]  ARCHITECTURE / HOW IT WORKS
  Quick visual: Image → AI → Rules → Action
  Mention: "The AI identifies. The rules decide.
   Hazardous items always get safety overrides."
  → Builds trust with technical judges.

[2:45–3:00]  CLOSING
  "WasteVisor — Know Before You Throw."
  Show logo. End.
```

### Why this works:
- **Two items, not five.** Judges lose attention after the second demo.
- **Smartphone is the hero.** It demonstrates the most complex, most impressive path (multi‑action, safety warning, resale suggestion).
- **Banana peel is the contrast.** It proves the system is not hard‑coded for electronics.
- **Architecture slide builds credibility** — shows this is not just an LLM wrapper.

---

## 8. AWS

### Current docs mention: Google Vision API, Google Cloud, Firestore, BigQuery. No AWS.

### Honest assessment: Does this MVP need AWS?

**For the hackathon prototype: probably not.** The entire app can run as:
- A static front‑end (local Vite dev server or a single S3 + CloudFront deployment)
- A single API call to a multimodal LLM (Claude/GPT/Gemini — none require AWS)

### Minimum credible AWS architecture (if AWS is required by hackathon rules):

```
┌─────────────────────────────────────────────────┐
│                   CloudFront                     │
│              (CDN for static assets)             │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │    S3 Bucket        │
        │ (React build output)│
        └─────────────────────┘
                   │
        ┌──────────┴──────────┐
        │  API Gateway (HTTP) │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │   Lambda Function   │
        │ (proxy to LLM API + │
        │  rule engine logic) │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │  Amazon Bedrock     │
        │ (Claude Sonnet for  │
        │  image analysis)    │
        └─────────────────────┘
```

**Services used (4 total):**
| Service | Purpose | Justification |
|---------|---------|---------------|
| **S3** | Host static React build | Standard, free‑tier eligible |
| **CloudFront** | CDN, HTTPS | Required for S3 website hosting with custom domain |
| **API Gateway + Lambda** | Serverless API proxy | No server to manage, scales to zero, free‑tier eligible |
| **Amazon Bedrock** | Multimodal LLM (Claude) for image analysis | Native AWS AI service, no API key management, IAM‑authenticated |

**Services explicitly NOT recommended:**
| Service | Why not |
|---------|---------|
| DynamoDB | No persistence needed for MVP. localStorage is sufficient. |
| Cognito | No auth needed for a demo. |
| SageMaker | We're not training a model. |
| Step Functions | One Lambda is enough. |
| ECS/EKS | Serverless is simpler. |

### If AWS is NOT required: skip it entirely. Run Vite locally and call the LLM API directly from a thin local proxy or even from the browser (with an API key in env).

---

## 9. UX

### Information hierarchy (result screen):

```
1. ITEM IDENTIFICATION    (what is it?)         — largest, top
2. BEST ACTION            (what should I do?)   — primary CTA, highlighted
3. SAFETY WARNING          (if hazardous)        — red/orange alert, unmissable
4. ALTERNATIVE ACTIONS     (what else could I do?) — secondary, below
5. EXPLANATION             (why this action?)    — small text, collapsible
6. DISCLAIMER              (legal/safety)        — footer, always present
```

### Primary CTA:
The upload button must be the single most prominent element on the landing screen. After results load, the "Best Action" card must be the focal point.

### Critical UX rules:

| Principle | Implementation |
|-----------|----------------|
| **Don't make users think** | The result screen should be scannable in 3 seconds. Item → Action → Done. |
| **Warnings must be impossible to miss** | Red/orange banner, ⚠ icon, bold text. Never a small footnote. |
| **No jargon** | "Compost this at home" not "Biodegradable organic matter suitable for aerobic decomposition" |
| **Low‑literacy friendly** | Use icons alongside text for every action (♻ recycle, 🔧 repair, 💰 sell, 🎁 donate, 🗑 dispose, ⚠ hazardous) |
| **One primary action** | Don't show 7 equal options. Show ONE best action prominently, rest as smaller alternatives. |
| **Loading state** | Show a skeleton/spinner while AI processes. 2–5 seconds is expected — show progress. |
| **Error state** | "We couldn't identify this item. Try a clearer photo or tell us what it is." — never a raw error. |

### Accessibility:
- Minimum contrast ratio: 4.5:1 (WCAG AA)
- All interactive elements focusable via keyboard
- Alt text on all images
- Screen‑reader friendly action cards

### Localization / audio (post‑MVP):
- Not for the hackathon, but the architecture should not hard‑code English strings in components. Use a constants file.

---

## 10. HACKATHON JUDGE PERSPECTIVE

### "What would make me remember WasteVisor after 30 projects?"

1. **The AI actually works on an arbitrary image.** Not a canned demo. I take a photo of something on my desk and it gives me a real answer. That's memorable.
2. **The safety override.** Showing that WasteVisor *refuses* to recommend donating a leaking battery — and instead shows a red warning — demonstrates engineering maturity.
3. **The thesis is tight.** "Know Before You Throw" is sticky. If I remember the tagline, I remember the product.
4. **The UI is beautiful.** In a sea of Bootstrap dashboards, a glassmorphic, animated, dark‑themed UI stands out.

### Biggest reasons I might REJECT WasteVisor:

| Risk | Likelihood | Impact |
|------|-----------|--------|
| "It's just a ChatGPT wrapper" — if the demo looks like an LLM chat with a pretty skin | HIGH if architecture is not explained | FATAL |
| Mock/fake AI results — if results are obviously pre‑baked | HIGH with current stub plan | FATAL |
| No safety handling — if a battery gets "donate it!" recommendation | MEDIUM | SEVERE |
| Overpromising — if UI claims carbon savings, resale prices, or regulatory compliance without data | MEDIUM | MODERATE |
| Too many features, none polished — if inventory, scoring, and history are all half‑built | HIGH with current plan | SEVERE |

### How to immunize against "just a wrapper":
The rule engine is the answer. In the demo, explicitly say:
> "The AI identifies the item. But the recommendation comes from a deterministic rule engine with safety overrides. We don't let the LLM decide what's hazardous."

That single sentence separates WasteVisor from every "I plugged an image into GPT" project.

---

## 11. ARCHITECTURE RISKS

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Express backend is unnecessary complexity** | HIGH | Eliminate. Use a single Lambda or call LLM from front‑end via thin proxy. |
| **Mock vision stub will kill credibility** | CRITICAL | Use a real multimodal LLM API. One API call replaces the entire mock. |
| **react-router for a single‑page app** | LOW | Remove. Use conditional rendering. |
| **localStorage for "tracking"** | LOW | Acceptable for MVP. Don't over‑invest. |
| **Vanilla CSS without a design system file** | MEDIUM | Create a single `design-tokens.css` file with all variables. Prevents inconsistency. |
| **Recommendation engine as a flat priority list** | HIGH | Implement as a decision tree with hazardous overrides. |
| **No error handling for LLM failures** | HIGH | Add timeout, retry, and fallback UI ("try again" + manual item entry). |
| **Over-scoping (history, analytics, dark mode, i18n)** | HIGH | Cut per Section 2. Focus on the core loop. |
| **No API key management strategy** | MEDIUM | Use environment variables. Never commit keys. |

---

## 12. FINAL RECOMMENDATION

### A. FINAL MVP (build exactly this, nothing more)

1. **Single‑page React app** (Vite, no router)
2. **Image upload** (drag‑drop + file picker)
3. **Real AI identification** via multimodal LLM API call (Amazon Bedrock/Claude, or direct API)
4. **Structured JSON response** from LLM (item, material, condition, category, hazardous flag)
5. **Deterministic rule engine** (decision tree, not flat list; hazardous override)
6. **Result screen** with: best action (prominent), alternatives (secondary), safety warning (if applicable), brief explanation
7. **Global safety disclaimer** in footer
8. **Polished UI** with one theme (dark preferred), glassmorphism cards, Inter font, micro‑animations

### B. NON‑MVP (build only if core is done and polished)

- Waste Inventory / history list
- Impact summary (qualitative only — "You've diverted 5 items from landfill")
- Camera capture
- Dark/light mode toggle

### C. RECOMMENDED ARCHITECTURE

```
[ Browser — Vite + React SPA ]
        │
        │  POST /api/analyze  (image as base64)
        ▼
[ Thin API layer ]  ← Lambda, or local Express if AWS not required
        │
        │  Multimodal LLM call (structured output)
        ▼
[ Amazon Bedrock / Claude API ]
        │
        │  { item, material, condition, category, hazardous, reusable, compostable }
        ▼
[ Rule Engine — deterministic JS module, runs in Lambda or browser ]
        │
        │  Ranked actions with metadata
        ▼
[ Browser renders result ]
```

- **Total services:** React + 1 API endpoint + 1 LLM provider
- **Total backend code:** ~100 lines (proxy + rule engine)
- **No database, no auth, no routing framework**

### D. RECOMMENDED IMPLEMENTATION ORDER

| Order | Task | Est. time | Why this order |
|-------|------|-----------|----------------|
| 1 | **Design system** (CSS variables, fonts, base layout) | 1 hr | Everything else builds on this. |
| 2 | **Upload component** (drag‑drop, file picker, preview) | 1.5 hr | Core input. Must be rock‑solid. |
| 3 | **API proxy** (thin endpoint that calls LLM with image) | 1.5 hr | Unblocks real AI results. |
| 4 | **LLM prompt engineering** (structured JSON output) | 1 hr | Get the identification quality right. |
| 5 | **Rule engine** (decision tree, hazardous overrides) | 2 hr | The product's brain. |
| 6 | **Result screen** (action cards, warnings, explanation) | 2 hr | The "wow" screen. |
| 7 | **Loading, error, and empty states** | 1 hr | Polish. |
| 8 | **End‑to‑end testing with real images** | 1 hr | Validate the full loop. |
| 9 | **UI polish** (animations, transitions, responsive) | 2 hr | Make it demo‑ready. |
| 10 | **Demo rehearsal and recording** | 2 hr | The deliverable. |
| — | **Total** | **~14 hr** | Leaves buffer for debugging. |

### E. TOP 5 RISKS

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| 1 | LLM API is down or rate‑limited during demo | Demo fails | Pre‑cache 2–3 results as fallback; have a recorded backup video |
| 2 | LLM returns garbage for unusual items | Credibility lost | Add confidence score; show "I'm not sure" for low confidence |
| 3 | Scope creep into history/analytics/scoring | Core loop unpolished | Hard rule: no new features after hour 12 |
| 4 | CSS inconsistency (no design system) | Looks amateur | Create design tokens first, before any components |
| 5 | Hazardous item gets unsafe recommendation | Safety/trust failure | Hard‑coded overrides in rule engine that cannot be bypassed by LLM |

### F. ACCEPTANCE CRITERIA FOR THE MVP

| # | Criterion | Pass condition |
|---|-----------|---------------|
| AC1 | User can upload any photo from their device | File picker opens, image previews, no errors |
| AC2 | AI returns a structured identification within 10 seconds | JSON with item, material, condition, category, hazardous flag |
| AC3 | Rule engine produces ranked actions | At least 1 primary action + 0–3 alternatives displayed |
| AC4 | Hazardous items show safety warning | Upload a battery photo → red warning banner appears, no "reuse/donate" suggestions |
| AC5 | Result screen is visually polished | Glassmorphism cards, consistent typography, no layout breaks on mobile |
| AC6 | Error states are handled gracefully | Disconnect network → friendly error message, not a crash |
| AC7 | Full demo flow completes in under 30 seconds per item | Upload → result in <10s, judge can read result in <20s |
| AC8 | Safety disclaimer is visible | Footer text present on every screen |

### G. WHAT THE NEXT CODING AGENT SHOULD BUILD FIRST

**Build order for the first coding session:**

```
1.  Initialize Vite + React project (no TypeScript for speed, no router)
2.  Create design-tokens.css (all CSS custom properties, fonts, colours)
3.  Create index.css (global resets, body styles, layout grid)
4.  Build the App shell (single page: header + main + footer)
5.  Build UploadCard component (drag-drop zone, file picker, image preview)
6.  Create server/ directory with a single proxy endpoint
7.  Write the LLM prompt (system prompt that returns structured JSON)
8.  Build ResultPanel component (hero action card + alternatives + warning)
9.  Wire upload → API call → result render
10. Test with a real image
```

**Do NOT start with:** the backend, the rule engine in isolation, routing, state management, or any "nice to have" feature. The upload → result screen is the atomic unit of value. Get it working end‑to‑end first, then layer in the rule engine and polish.

---

*Review complete. No application code was written. All findings are documented for the implementing agent.*
