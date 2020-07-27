from notion.client import NotionClient
from typing import *


class NotionAPI:
    def __init__(self, token) -> None:
        if token == None:
            raise Exception("Token not found.")

        self.client = NotionClient(
            token_v2=token, monitor=True, start_monitoring=True, enable_caching=False)

    def get_client(self):
        return self.client

    def current_space(self):
        return self.client.current_space

    def _get_resource(self, key: str, collection: List[Any]):
        resource = None

        for block in collection:
            if hasattr(block, 'title') and block.title.lower() == key:
                resource = block

        if resource is None:
            raise Exception(f"No {key} block found.")

        return resource

    def get_workbench(self):
        key = 'workbench'
        source = self.client.get_top_level_pages()
        workbench = self._get_resource(key, source)

        return workbench

    def get_projects(self):
        key = 'projects'
        workbench = self.get_workbench()

        source = workbench.children
        projects = self._get_resource(key, source)

        return projects

    def get_tasks(self):
        key = 'tasks'
        workbench = self.get_workbench()

        source = workbench.children
        tasks = self._get_resource(key, source)

        return tasks
