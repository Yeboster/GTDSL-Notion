from notion.client import NotionClient
from typing import *


class NotionAPI:
    def __init__(self, token) -> None:
        if token == None:
            raise Exception("Token not found.")

        self.client = NotionClient(
            token_v2=token, monitor=True, start_monitoring=True, enable_caching=False)

    def current_space(self):
        return self.client.current_space

    def get_resource(self, key: str, collection: List[Any]):
        resource = None

        for block in collection:
            if hasattr(block, 'title') and block.title.lower() == key:
                resource = block

        if resource is None:
            raise Exception(f"No {key} block found.")

        return resource