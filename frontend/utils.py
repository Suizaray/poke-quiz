import requests

API_URL = "http://localhost:8000"

def api_get(path, params=None):
    r = requests.get(f"{API_URL}{path}", params=params)
    r.raise_for_status()
    return r.json()

def api_post(path, json=None):
    r = requests.post(f"{API_URL}{path}", json=json)
    r.raise_for_status()
    return r.json()
