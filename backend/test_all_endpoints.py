import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

endpoints = [
    ("GET", "/", None),
    ("GET", "/health", None),
    ("GET", "/system/status", None),
    ("GET", "/system/version", None),
    ("GET", "/metrics", None),
    ("GET", "/integrity", None),
    ("GET", "/architecture", None),
    ("GET", "/diagnostics", None),
    ("GET", "/pipeline/history", None),
    ("POST", "/pipeline/run", {"account_id": 101, "auto_approve_hitl": True, "prompt": "Test pipeline run"}),
    ("GET", "/agents", None),
    ("GET", "/agents/data_collector_agent", None),
    ("GET", "/agents/data_collector_agent/status", None),
    ("GET", "/policies", None),
    ("GET", "/policies/schema", None),
    ("GET", "/policies/data_collector_agent", None),
    ("POST", "/policies/validate", {"policy_yaml_content": "agent_id: test_agent\npolicy_version: '1.0'\napproved_models: ['openai/gpt-oss-120b']\nallowed_tools: []\ndenied_scopes: []\nguardrails:\n  pii_protection: true\n  prompt_injection_protection: true\n  harmful_content_filter: true\nhitl:\n  enabled: true\n  risk_threshold: 0.7\n  high_risk_requires_approval: true\ndata_access:\n  pii_allowed: false\n  allowed_tables: []\ndata_retention:\n  reports_days: 90\n  audit_logs_days: 365\nregulatory_frameworks: ['internal']\nrate_limits:\n  max_calls_per_tool: 3\naudit:\n  enabled: true\n  log_inputs: true\n  log_outputs: true\n  log_denied_actions: true\n"}),
    ("GET", "/versions", None),
    ("GET", "/versions/current", None),
    ("GET", "/versions/1", None),
    ("GET", "/audit", None),
    ("GET", "/audit/export", None),
    ("POST", "/audit/search", {"limit": 10}),
    ("GET", "/reports", None),
    ("GET", "/stats/agents", None),
    ("GET", "/stats/tools", None),
    ("GET", "/demo/tools", None),
]

results = []

for method, path, body in endpoints:
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if body else {}
    data = json.dumps(body).encode("utf-8") if body else None
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            status = response.status
            results.append({
                "method": method,
                "path": path,
                "status": status,
                "ok": True,
                "response": res_body[:200]
            })
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        results.append({
            "method": method,
            "path": path,
            "status": e.code,
            "ok": False,
            "error": err_body[:300]
        })
    except Exception as e:
        results.append({
            "method": method,
            "path": path,
            "status": 0,
            "ok": False,
            "error": str(e)
        })

print(json.dumps(results, indent=2))
