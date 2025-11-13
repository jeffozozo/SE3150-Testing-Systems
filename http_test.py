import requests

response = requests.get("http://localhost:8080/squirrels")

print("Status code:", response.status_code)      # e.g. 200
print("Headers:", response.headers)              # response headers
print("Body:", response.text[:200])
