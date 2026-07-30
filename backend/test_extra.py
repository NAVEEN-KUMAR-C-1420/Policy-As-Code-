import json
import urllib.request
import urllib.error

BASE_URL = 'http://127.0.0.1:8000'

endpoints = [
    ('GET', '/pipeline/status/1', None),
    ('POST', '/policies/deploy', {'agent_id': 'data_collector_agent', 'policy_yaml_content': 'test'}),
    ('POST', '/versions/1/rollback', None),
    ('GET', '/reports/1', None),
    ('GET', '/reports/download/1', None),
    ('POST', '/demo/tool/toggle', {'tool_key': 'test', 'enabled': True}),
    ('POST', '/demo/safemode/toggle', {'enabled': True}),
    ('POST', '/demo/run-sample', None),
    ('POST', '/demo/reset', None),
]

results = []
for method, path, body in endpoints:
    url = f'{BASE_URL}{path}'
    headers = {'Content-Type': 'application/json'} if body else {}
    data = json.dumps(body).encode('utf-8') if body else None
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            results.append({'path': path, 'status': response.status, 'response': res_body[:200]})
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8') if e.fp else ''
        results.append({'path': path, 'status': e.code, 'error': err_body[:300]})
    except Exception as e:
        results.append({'path': path, 'status': 0, 'error': str(e)})

print(json.dumps(results, indent=2))
