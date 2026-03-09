import requests

url = "http://localhost:8000/users/"


payload = {
    'name':'thomas',
    'email':'admin@admin.com',
    'password':'admin'
}


headers = {
    "Content-Type": "application/json"
}


response = requests.post(url, json=payload, headers=headers)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("Respuesta:")
    print(data)
else:
    print("Error:")
    print(response.text)