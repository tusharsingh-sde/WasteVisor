# Agents Overview

This document provides a concise overview of the autonomous agents and tooling that constitute the **WasteVisor** development environment during the hackathon.

## Primary Development Agent – **Antigravity**
- **Role**: Lead software architect, senior engineer, and pair‑programming assistant.
- **Capabilities**:
  - Inspects repository structure.
  - Generates design documentation (PROJECT_CONTEXT, PLAN, architecture, decisions, etc.).
  - Writes, edits, and creates code files using the provided tooling.
  - Executes commands, runs builds, and monitors background tasks.
  - Interacts with external services (e.g., image‑analysis APIs) through MCP tools.
- **Interaction Model**: Works interactively with the human hackathon participant, asking clarification questions only when needed.

## Supporting Agents (MCP Tools)
| Agent | Server | Purpose |
|------|--------|---------|
| `data-agent-kit.get_active_editor_context` | data-agent-kit | Retrieves the current editor context for smart edits. |
| `notebook-guidance` (skill) | – | Guides creation of Jupyter notebooks for data exploration, if required. |
| `visualization.render_chart` | visualization | Generates charts/graphics for documentation and demo. |
| `gcp-data-pipelines` (skill) | – | Helps design data pipelines for any backend services (not used in the MVP). |
| `google-cloud-auth-verification` (skill) | – | Ensures proper authentication for any Google Cloud integration. |

## Tooling Stack
- **File Operations** – `view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`.
- **Command Execution** – `run_command` for installing dependencies, starting dev servers, etc.
- **Background Management** – `manage_task` and `schedule` to monitor long‑running processes (e.g., dev server). 
- **Knowledge Integration** – Use **Knowledge Items (KI)** to locate existing patterns; not required for this fresh repo.

## Agent Workflow for the Hackathon
1. **Repository Scan** – Antigravity lists the workspace to assess existing code.
2. **Documentation Generation** – Creates the required markdown files (PROJECT_CONTEXT, AGENTS, PLAN, architecture, decisions).
3. **Rapid Prototyping** – Sets up a Vite‑React front‑end, a lightweight Node/Express backend, and integrates a placeholder AI model.
4. **Demo Preparation** – Generates a polished UI mockup, scripts demo flow, and records a short video.
5. **Iterative Feedback** – The human partner reviews each artifact; Antigravity refines based on input.

---
*All agent interactions are logged under the conversation ID for traceability.*
