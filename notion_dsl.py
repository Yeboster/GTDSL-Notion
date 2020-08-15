import logging
from dataclasses import dataclass
from typing import *

from notion.block import TextBlock
from notion.collection import NotionDate, Collection, CollectionRowBlock

logger = logging.getLogger(__name__)


@dataclass
class Project:
    """Class to represent notion GTD project"""
    id: str = None
    title: str = None


@dataclass
class Task:
    """Class to represent notion GTD task"""
    id: str = None
    title: str = None
    # TODO: Improve name semantics
    project_name: str = None
    assigned_project: Project = None
    scheduled: NotionDate = None
    url: str = None
    status: str = None
    context: str = None
    convert: bool = False
    _inserted: bool = False

    def apply_properties_from(self, properties: Dict[str, str]) -> None:
        keys = ['scheduled', 'status', 'context', 'url', 'convert']
        for key in keys:
            value = properties[key]
            setattr(self, key, value)

    def dict_to_insert(self) -> Dict[str, Any]:
        keys = ['title', 'project', 'scheduled', 'url', 'status', 'context']
        insert_dict: Dict[str, Any] = {}
        for key in keys:
            if key == 'project':
                if prj := self.assigned_project:
                    insert_dict['project'] = prj.id
            else:
                insert_dict[key] = getattr(self, key)

        return insert_dict

    def assign_or_create_project_from(self, projects_col: Collection) -> None:
        """Get project based on name. If found it returns a Project GTD wrapper"""
        project: Project = None
        if self.project_name and projects_col and not self.assigned_project:
            for proj in projects_col.get_rows():
                title: str = proj.title
                if title and title.lower().find(self.project_name) > -1:
                    # TODO: Find multiple projects
                    project = Project(proj.id, proj.title)
                    break

            if project is None:
                logging.debug('Create project since no one found.')
                notion_project: Project = projects_col.add_row(
                    update_views=False)
                notion_project.title = self.project_name
                notion_project.stage = '💡Idea'

                project = Project(notion_project.id, notion_project.title)

            self.assigned_project = project

    def insert_into(self, tasks_col: Collection, force=False) -> None:
        """Insert task into collection if not existing"""
        if tasks_col and (not self._inserted or force):
            created_task: CollectionRowBlock = tasks_col.add_row(
                update_views=False)

            for key, value in self.dict_to_insert().items():
                logging.debug(f"{key} -> {value}")

                setattr(created_task, key, value)

            logging.debug(
                f"Created task properties: {created_task.get_all_properties()}")

    def post_creation_action(self, inbox_block: CollectionRowBlock) -> None:
        """Run all the actions after creating GTD task."""
        inbox_block.convert = False
        task_title = inbox_block.title
        inbox_block.title = "✅ " + task_title
        content = f"Added task to **'{self.assigned_project.title}'** project." if self.assigned_project else f"Task added without project."
        inbox_block.children.add_new(TextBlock, title=content)


def decode_dsl(id: str, content: str, properties: Dict[str, str]) -> Task:
    task: Task = Task(id)
    if (pos := content.find(':')) > -1:
        task.title = content[pos+1:].strip().capitalize()
        task.project_name = content[:pos].strip().capitalize()
    else:
        task.title = content.strip().capitalize()

    task.apply_properties_from(properties)

    return task
