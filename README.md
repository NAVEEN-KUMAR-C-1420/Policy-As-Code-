# Finance Multi-Agent Pipeline with AI Governance (Policy-as-Code)

## What is Policy-as-Code?
Policy-as-Code means defining security, governance, and compliance rules in structured files (like YAML) that live alongside your application code. Instead of relying on system prompts—which are easily bypassed—these rules are automatically validated and strictly enforced by middleware at runtime.

## What this project demonstrates
This project implements a complete local execution of an **agent + policy governance runtime**. It demonstrates how to separate an agent's configuration (what it *wants* to do) from its governance policy (what it is *permitted* to do), and how to enforce those boundaries strictly before and during execution using a centralized Tool Interceptor.

## Three-Agent Architecture
The pipeline consists of three sequential agents:

1. **Data Collector Agent** (Read-Only): Reads raw account transactions and fetches relevant market news using Tavily.
2. **Risk Analyzer Agent** (Read & Compute): Reads account summaries and deterministically calculates a risk score (using standard math, not LLM arithmetic) based on outflows.
3. **Report Writer Agent** (Write-Only): Consolidates data and risk findings into a final report, saving it to SQLite and a Markdown file. It is explicitly blocked from deleting data.

## `agent.yaml` vs `policy.yaml`
- **`agent.yaml` (Configuration):** Defines what the agent is technically configured to use (e.g., name, description, model, temperature, max_tokens, requested tools).
- **`policy.yaml` (Governance):** Defines the boundaries of what the agent is allowed to do. It sets approved models, explicitly allowed tools, denied scopes, data access limits, rate limits, and HITL thresholds. **Default behavior is DENY.**

## Policy Schema & Validation
Every agent must adhere to a strict policy schema, which includes:
- `agent_id` and `policy_version`
- `approved_models` (List of allowed LLMs)
- `allowed_tools` (Tools allowed, their scope, target resource, and tables)
- `denied_scopes` (Scopes the agent must never access, e.g., `delete`)
- `guardrails` (PII protection, harmful content filters)
- `hitl` (Human-in-the-loop thresholds)
- `data_access` (Table-level restrictions and PII rules)
- `data_retention` (Data lifecycle policies)
- `regulatory_frameworks` (Compliance tags)
- `rate_limits` (Execution limits per tool)
- `audit` (Logging preferences)

The **Policy Validator** (`middleware/policy_validator.py`) strictly checks this schema before any agent can start. Missing fields, invalid types, or negative retention limits will block the agent.

## Runtime Enforcement
Governance is strictly enforced by `middleware/tool_interceptor.py`:
- Every tool call is intercepted.
- If a tool is unknown or not explicitly allowed in `policy.yaml`, it is **blocked**.
- If a tool falls under a `denied_scope`, it is **blocked** (deny takes precedence).
- If rate limits are exceeded, it is **blocked**.
- Every decision (ALLOWED, DENIED, RATE_LIMITED) is recorded.

## Approved Models
At startup, `middleware/agent_policy_compat.py` checks that the model requested in `agent.yaml` exists within the `approved_models` list in `policy.yaml`. If an agent tries to use an unapproved model, startup fails immediately.

## Tool Scopes
Policy distinguishes tools by `scope` (e.g., `read`, `write`, `compute`, `delete`). For example, the `Report Writer Agent` has `delete` listed in its `denied_scopes`. Even if a delete tool were somehow granted `allowed: true` by mistake, the denied scope rule would override and block the execution.

## HITL (Human-in-the-Loop)
Risk calculations are deterministic. If the `Risk Analyzer Agent` calculates a risk score exceeding the policy's `risk_threshold` (e.g., `0.70`), the pipeline halts### 3. Start the Server

```bash
uvicorn api.main:app --reload
```
Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to view the API Swagger UI.

## API Testing

A complete test suite is available in the `api_testing/` directory, built using `pytest` and FastAPI's `TestClient`. It executes against the actual endpoints without mocking.

```bash
# Run all tests
pytest api_testing/ -v
```

## Database Support

The project natively supports both local **SQLite** and remote **PostgreSQL (Supabase)**.

Switch databases by configuring your `.env` file:

```env
DATABASE_PROVIDER=sqlite
# or
DATABASE_PROVIDER=supabase

SUPABASE_DB_HOST=your-host.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
```

## CI/CD Architecture & Deployment Flow

This project features a fully automated CI/CD pipeline using **GitHub Actions**, orchestrated inside the `.github/workflows/` directory.

### 1. Continuous Integration (`ci.yml`)
Runs automatically on every Push and Pull Request to the `main` branch. It strictly enforces:
- Python syntax compilation
- Dependency installation
- API test execution (`api_testing/`)
- Legacy Governance validation (`test_governance.py`)
If any of these fail, the build is blocked.

### 2. Security Scans (`security.yml`)
Runs TruffleHog secrets scanning to ensure no LLM keys (Groq/Anthropic), database passwords, or `.env` files are accidentally committed.

### 3. Continuous Deployment (`deploy.yml`)
Upon a successful CI pipeline run on the `main` branch, the deployment workflow triggers a web hook to update the live production environment. It then waits for the server to spin up and verifies the live `/health` and `/system/status` endpoints.

## Required Secrets & Environment Variables

### GitHub Secrets
To allow GitHub Actions to deploy to your hosting provider (e.g., Render), add the following in `Settings > Secrets and variables > Actions`:
- **`RENDER_DEPLOY_HOOK_URL`**: (Secret) Webhook URL provided by Render to trigger the build.
- **`PRODUCTION_API_URL`**: (Variable) URL of your live API, e.g., `https://myapp.onrender.com`.

### Production Variables (Render/Host)
Inside your cloud hosting environment dashboard, you must provide the following:
- `DATABASE_PROVIDER=supabase`
- `SUPABASE_DB_HOST=postgresql://postgres.xxx...`
- `SUPABASE_DB_PORT=5432`
- `SUPABASE_DB_NAME=postgres`
- `SUPABASE_DB_USER=postgres`
- `SUPABASE_DB_PASSWORD=your_password`
- `GROQ_API_KEY=gsk_yourkey`
- `TAVILY_API_KEY=tvly-yourkey`

## Immutable Policy Versioning & Rollback

Every time a new policy is deployed via the `/policies/deploy` endpoint, the system guarantees an **immutable version history** in Supabase:
- **Never Overwritten:** The existing active policy is retained as a historical artifact with its unique SHA hash.
- **Always Tracked:** The newest policy deployed automatically becomes active.
- **Audit Ready:** An audit log event is generated capturing who deployed the policy and when.
- **Instant Rollback:** You can instantly revert to a previous policy using the `/policies/{agent_id}/rollback` endpoint by providing the target version SHA.

## Data Access & PII Controls
Tools declare which SQLite tables they access and whether they handle PII. If `policy.yaml` restricts an agent to specific `allowed_tables` (e.g., only `transactions`) or sets `pii_allowed: false`, any tool violating these constraints is blocked at runtime.

## Data Retention
The `middleware/data_retention.py` module provides deterministic functions to identify and clean up old database reports and audit logs based on the policy's `data_retention` values (e.g., `reports_days: 90`). Dangerous deletion functions must be manually invoked and are governed to prevent accidental data loss.

## Audit Logging
Every governance event is recorded as a JSONL entry in `logs/audit_log.jsonl`. This includes tool calls, model checks, HITL checks, and policy validation results. Crucially, raw PII and API keys are never logged.

## Database Schema
The dummy SQLite database (`data/finance.db`) contains three tables:
- `accounts`: account_id, customer_name, account_type, balance
- `transactions`: transaction_id, account_id, txn_date, amount, category, description
- `reports`: report_id, account_id, created_at, summary

## Setup & Execution

### 1. Initialize the Database
```bash
python data/init_db.py
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
Copy `.env.example` to `.env` and fill in your API keys (e.g., `GROQ_API_KEY`, `TAVILY_API_KEY`).

### 4. Run Governance Tests (No API Keys Required)
The test suite proves the middleware works, even offline.
```bash
python test_governance.py
```

### 5. Run the Full Pipeline
```bash
python orchestrator/run_pipeline.py
```


