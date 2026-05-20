import requests
resp = requests.post("http://localhost:8000/agent/sql", json={"question": "List all products"})
print(resp.json())