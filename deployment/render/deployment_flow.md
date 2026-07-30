# Deployment Flow

1. **GitHub Push:** Code is pushed to the `main` branch.
2. **GitHub Actions:** The CI/CD pipeline triggers and runs `python scripts/verify_project.py` (The Single Source of Truth).
3. **Validation:** If verification fails, the pipeline halts. No deployment occurs.
4. **Render Auto-Deploy:** If verification succeeds, Render detects the successful commit (via integration) and starts a new build.
5. **Render Build:** Render pulls the code and executes `pip install -r requirements.txt`.
6. **Render Start:** Render executes `uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
7. **Health Check:** Render monitors the `/health` endpoint to determine when the application is actively accepting traffic.
8. **Live:** The new container routes active traffic. Old containers are spun down.
