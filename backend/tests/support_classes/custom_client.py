import requests

from utils.utils import get_config, get_token


class CustomClient:
    def __init__(self):
        self.config = get_config()
        self.site = self.config["site"]
        self.get_token = get_token()
        self.headers = {}

    def get_headers(self):
        self.headers['Content-Type'] = self.config['headers']
        if self.authenticated:
            self.headers['Authorization'] = self.get_token()
        return self

    def nonauth_user(self):
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
            self.authenticated = False
        return self

    def post(self, site, data):
        return requests.post(site, headers=self.headers, data=data)

    def get(self, path):
        return requests.get(f'{self.site}/{path}', headers=self.headers)

    def patch(self, site, data):
        return requests.patch(site, headers=self.headers, data=data)

    def delete(self, site):
        return requests.get(site, headers=self.headers)
