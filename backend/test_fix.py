import json
import urllib.request

BASE_URL = 'http://127.0.0.1:8000'

try:
    req = urllib.request.Request(f'{BASE_URL}/demo/run-sample', method='POST')
    with urllib.request.urlopen(req) as response:
        print('/demo/run-sample STATUS:', response.status)
        print('/demo/run-sample BODY:', response.read().decode('utf-8')[:100])
except Exception as e:
    print('/demo/run-sample ERROR:', e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
