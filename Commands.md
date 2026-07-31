 ## Create a new virtual environment

## From the backend directory:

cd backend
python -m venv .venv

## Activate it:

Windows
.\.venv\Scripts\activate

## Install backend requirements

pip install --upgrade pip
pip install -r requirements.txt

## Verify backend

python scripts/verify_project.py
python tests/run_all_tests.py
python -c "import sys; sys.path.insert(0, 'app'); from api.main import app; print('Backend Import Successful')"
uvicorn app.api.main:app --reload

 ## Open

http://127.0.0.1:8000/docs
and
http://127.0.0.1:8000/health

## Frontend

## Open another terminal.

cd frontend
npm install

## Start

npm run dev

http://localhost:5173

## Running Backend Only

.\.venv\Scripts\activate
uvicorn api.main:app --reload

## Running Frontend Only

cd frontend
npm install
npm run dev


## Running Both Together


## Terminal 1

cd backend
.\.venv\Scripts\activate
uvicorn api.main:app --reload

## Terminal 2

cd frontend
npm run dev

## End points 

HTTP Method: GET

Complete Endpoint Path: /policies/{agent_id}/versions/{commit_sha}

Request Parameters:
agent_id (path parameter, string): ID of the agent (e.g. data_collector_agent, master_agent).
commit_sha (path parameter, string): Git commit SHA (e.g. HEAD, a1b2c3d4) or database release SHA (local_sqlite_head).

## Sample curl Request:

bash
curl -X GET "http://127.0.0.1:8000/policies/data_collector_agent/versions/HEAD"

## Sample Response 

{
  "success": true,
  "message": "Success",
  "data": {
    "metadata": {
      "agent_id": "data_collector_agent",
      "commit_sha": "HEAD",
      "policy_hash": "83d5acdbfc579bd4c74047ab82438c024a2cd355771de3377304de9719c2b16c",
      "deployed_at": null,
      "deployed_by": "git_history",
      "deployment_source": "git",
      "is_active": 0,
      "notes": "Retrieved from Git history"
    },
    "policy_yaml": "agent_id: data_collector_agent\npolicy_version: \"1.0\"...",
    "source": "git"
  },
  "errors": null
}


## To deploy a new version of an agent's policy:

bash
curl -X POST "http://127.0.0.1:8000/policies/deploy" \
-H "Content-Type: application/json" \
-d '{
  "agent_id": "data_collector_agent",
  "policy_yaml": "# Deployment content goes here...",
  "commit_message": "Initial deployment"
}'

### Prompts to use 

## Standard Risk Analysis :

Analyze account 101 and generate a complete financial risk report

## HITL (Human-in-the-Loop) Trigger :

Remove all flagged transactions for account 101 and shutdown the monitoring

## Full Report with Download :

Run a complete risk assessment for account 102 and prepare a downloadable governance report with all findings

## Governance Evaluation Demo :

Analyze account 101 — check transaction anomalies, compute risk score, and flag any compliance violations under internal-financial-governance policy

## PII Detection Demo:

My email is john@example.com — can you analyze account 102 for me?