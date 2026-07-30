# AIVAR: Enterprise Multi-Agent Financial Governance Platform

AIVAR is a production-grade multi-agent financial platform built with FastAPI, React, and Tailwind CSS. It enforces strict compliance boundaries, data safety rules, and real-time security scanning (PII & Prompt Injection) for autonomous AI agents using a dynamic **Policy-as-Code** governance framework.

---

## 1. Project Overview

AI agents are powerful but prone to hallucinations, data leakage, and prompt injections. AIVAR provides a **zero-trust execution environment** by decoupling an agent's configuration (what it *wants* to do) from its governance policy (what it is *permitted* to do).

Key capabilities demonstrated:
- 🛡️ **Presidio PII Shield**: Real-time identification and redaction of Names, Emails, Phone Numbers, Credit Cards, IP Addresses, and custom sensitive tokens before prompts reach LLM layers.
- 🛑 **Prompt Injection Shield**: Identifies and blocks jailbreaks and override patterns (`Ignore previous instructions`, `Reveal system prompt`).
- 🔐 **Code Integrity & Safe Mode**: Computes runtime SHA256 hashes of agent code, configurations, and YAML policies to lock down pipeline runs if unauthorized code modifications are detected.
- ⚙️ **Deterministic Governance**: Intercepts every tool request at runtime, blocking actions falling outside explicitly defined policy scopes or exceeding rate limits.
- 📜 **Immutable Audit Logging & Versioning**: Logs every agent decision, tool intercept, and policy change to a secure database. Supports version rollback.

---

## 2. Platform Architecture

```
User Prompt (React App)
   │
   ▼
FastAPI REST Layer
   │
   ├──► Presidio PII Shield & Prompt Injection Guard (Redaction & Safety checks)
   ├──► Code Integrity SHA256 Validator (Safe Mode verify)
   └──► Governance Middleware
         │
         ├──► Policy Engine (Enforces YAML boundaries & scopes)
         ├──► Version Control Repository (Active state matches)
         └──► Agent Router / Orchestrator
               │
               ├──► Data Collector Agent
               ├──► Risk Analyzer Agent
               └──► Report Writer Agent
                     │
                     ├──► Tool Interceptor (Intercepts all tool executions)
                     ├──► Audit Trail Logger (Immutably records actions)
                     └──► Supabase / SQLite Storage
```

---

## 3. Folder Structure

```
AIVAR/
├── backend/                  # FastAPI Application
│   ├── agents/               # 3 sequential AI Agents
│   ├── api/                  # Routers, REST services, and models
│   ├── common/               # Database, LLM loader, and shared repositories
│   ├── config/               # YAML provider configuration
│   ├── core/                 # Core paths config and path utilities
│   ├── data/                 # Database initialization and storage files
│   ├── middleware/           # Policy validators, audit loggers, PII & Integrity engines
│   ├── orchestrator/         # Agent run coordination pipeline
│   ├── scripts/              # CI verification framework
│   ├── tests/                # Unit and API pytest suites
│   ├── logs/                 # Output audit logs
│   ├── reports/              # Generated markdown risk reports
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React Frontend Application (Vite + Tailwind)
│   ├── src/
│   │   ├── components/       # Visual Timeline, Architecture Graph, and badges
│   │   ├── pages/            # Landing page, Dashboard, Versions, Health, Settings
│   │   └── services/         # Axios API backend connector client
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── vite.config.js        # Vite compilation proxy config
│
├── .github/
│   └── workflows/            # CI and Security Scan actions
├── .gitignore
├── .trufflehog.yml           # Secret scan exclusions config
├── LICENSE
└── README.md                 # Project Documentation (This file)
```

---

## 4. Installation & Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install pinned Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your API keys (e.g. `GROQ_API_KEY`, `TAVILY_API_KEY`):
   ```bash
   cp .env.example .env
   ```
5. Initialize the database schema:
   ```bash
   python data/init_db.py
   ```
6. Start the API backend:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

### Step 2: Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Launch the local Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## 5. Testing & Verification

Run the Python verification script and test suites to validate system health.

### Verify Project Structure and Environment
```bash
cd backend
python scripts/verify_project.py
```

### Run Unit and API Pytest Suites
```bash
cd backend
python tests/run_all_tests.py
# Or directly via pytest:
python -m pytest tests/ -v
```

---

## 6. Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PROVIDER` | Choose SQLite or Supabase database integration | `sqlite` |
| `GROQ_API_KEY` | Groq API credential for agent execution | Required |
| `TAVILY_API_KEY` | Tavily Web Search API key for data collection | Required |
| `OPENAI_API_KEY` | Optional OpenAI key for agent execution | - |

---

## 7. Future Deployment Guides

### Dockerization (Planned)
The AIVAR repository is designed for containerized deployment.
- **Backend Service**: Can be wrapped in a lightweight `python:3.10-slim` container exposing port `8000`, using Gunicorn or Uvicorn.
- **Frontend Service**: Can be built using standard Node base images, compiled to static assets (`dist/`), and served via an Nginx container on port `80`.

### Cloud Deployment (Planned)
- **Database**: Transition from local SQLite to secure Supabase / PostgreSQL.
- **Scaling**: Ready for deployment on AWS ECS, GCP Cloud Run, or Kubernetes (EKS/GKE) with separate deployment manifests.

---

## 8. Contribution Guidelines

Contributions are welcome. Please ensure:
1. All changes comply with policy and tool schema validator rules.
2. Code formatting is checked using `black` and `ruff`.
3. The project verification script (`python scripts/verify_project.py`) and all tests pass with a 100% success rate prior to staging a pull request.
