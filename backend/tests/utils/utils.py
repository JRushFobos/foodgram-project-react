import json
import requests


def get_config():
    file = 'settings/settings.json'
    with open(file) as f:
        return json.load(f)


def get_token():
    config = get_config()
    site = config["site"]
    headers = {'Content-Type': config["headers"]}
    body = config["body"]
    response = requests.post(
        f'{site}/api/auth/token/login/', headers=headers, data=body
    )
    print(response.status_code)
    print(response.json())
    token = response.json().get("auth_token")
    return f'Token {token}'
