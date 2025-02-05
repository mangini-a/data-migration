import requests
import json

url = "http://localhost:5000/receive"
data = {
    "table": "example_table",
    "columns": ["id", "name", "price"],
    "data": [
        {"id": 1, "name": "Product 1", "price": 10.99},
        {"id": 2, "name": "Product 2", "price": 20.99}
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
