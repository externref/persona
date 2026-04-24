import requests

requests.post("http://localhost:8000/api/v0/init", json="{\"hello\": \"world\"}")