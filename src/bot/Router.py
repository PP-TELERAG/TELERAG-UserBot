import httpx

from pyrogram import Client, filters  # noqa: F401


class BaseRouter:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)

    def get(self, endpoint: str, params: dict = None, headers: dict = None):
        response = self.client.get(endpoint, params=params, headers=headers)
        return response.json()

    def post(self, endpoint: str, data: dict = None, headers: dict = None):
        response = self.client.post(endpoint, json=data, headers=headers)
        return response.json()

    def put(self, endpoint: str, data: dict = None, headers: dict = None):
        response = self.client.put(endpoint, json=data, headers=headers)
        return response.json()

    def delete(self, endpoint: str, headers: dict = None):
        response = self.client.delete(endpoint, headers=headers)
        return response.json()

    def close(self):
        self.client.close()


class Router(BaseRouter):
    def __init__(self, base_url):
        super().__init__(base_url)
        pass

    # TODO: Методы которые будут отправлять запросы к API
