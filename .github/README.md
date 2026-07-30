# CI/CD and Deployment Architecture

This repository uses GitHub Actions for continuous integration, security scanning, and continuous deployment.

## Workflows

1. **CI Pipeline (`ci.yml`)**: Triggered on `push` and `pull_request` to `main`. It compiles the Python codebase, runs the FastAPI TestClient suite (`api_testing/`), and executes the core legacy governance tests (`test_governance.py`). If any check fails, the pipeline aborts.
2. **Security Scans (`security.yml`)**: Runs TruffleHog secret scanning to ensure no API keys (Groq, Anthropic, Supabase) are accidentally checked in. It also explicitly checks for a leaked `.env` file.
3. **Deploy Pipeline (`deploy.yml`)**: Automatically triggers when the CI pipeline succeeds on the `main` branch. It sends a webhook to Render to initiate the build. Afterwards, it runs automated HTTP status checks against the live production environment.

## Required GitHub Secrets

To make the deployment work, configure the following secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

- **`RENDER_DEPLOY_HOOK_URL`**: The deploy hook URL provided by your Render web service (Secret).
- **`PRODUCTION_API_URL`**: The base URL of your deployed application (Variable) - e.g. `https://finance-governance-api.onrender.com`.

## Required Production Variables (Render)

Inside the Render dashboard (or your cloud hosting provider), set the following Environment Variables:

- `DATABASE_PROVIDER=supabase`
- `SUPABASE_DB_HOST=postgresql://postgres.xxx...`
- `SUPABASE_DB_PORT=5432`
- `SUPABASE_DB_NAME=postgres`
- `SUPABASE_DB_USER=postgres`
- `SUPABASE_DB_PASSWORD=your_password`
- `GROQ_API_KEY=gsk_...`
- `TAVILY_API_KEY=tvly-...`

The API endpoints, SQLite mode, Supabase mode, policy versioning, and rollback mechanisms are automatically verified before every deployment.
