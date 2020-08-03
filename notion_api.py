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

    def get_projects_collection_view(self):
        key = 'projects'
        workbench = self.get_workbench()

        source = workbench.children
        cv = self._get_resource(key, source)
        projects = cv

        return projects

    def get_projects_views(self):
        return self.get_projects_collection_view().views


    def get_projects_rows(self):
        cv = self.get_projects_collection_view()

        return cv.collection.get_rows()

    def get_tasks_collection_view(self):
        key = 'tasks'
        workbench = self.get_workbench()

        source = workbench.children
        cv = self._get_resource(key, source)
        tasks = cv

        return tasks

    def get_tasks_views(self):
        return self.get_tasks_collection_view().views

    def get_tasks_rows(self):
        cv = self.get_tasks_collection_view()

        return cv.collection.get_rows()

    def filter_tasks_with_schedule(self):
        filter_params = [
            {
                "property": "schedule",
                "comparator": "is_not_empty"
            }
        ]

        result = self.get_tasks_views()[0].build_query(
            filter=filter_params).execute()
        return result
