import logging
from dataclasses import dataclass
from typing import *

from notion.block import TextBlock
from notion.collection import NotionDate, Collection, CollectionRowBlock

logger = logging.getLogger(__name__)


@dataclass
class Project:
    """Class to represent notion GTD project"""
    id: str
    title: str


@dataclass
class Task:
    """Class to represent notion GTD task"""
    id: str
    title: str
    project_name: str
    assigned_project: Project
    scheduled: NotionDate
    url: str
    status: str
    context: str
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

    def assign_or_create_project_into(self, projects_col: Collection) -> None:
        """Get project based on name. If found it returns a Project GTD wrapper"""
        project: Project = None
        if self.project_name and projects_col and not self.assigned_project:

            if found_project := _find_resource(self.project_name, projects_col):
                project = Project(found_project.id, found_project.title)

            if project is None:
                logging.warning('Create project since no one found.')
                notion_project: CollectionRowBlock = projects_col.add_row(
                    update_views=False)
                notion_project.title = self.project_name
                notion_project.stage = '💡Idea'

                project = Project(notion_project.id, notion_project.title)

            self.assigned_project = project

    def insert_into(self, tasks_col: Collection) -> None:
        """Insert task into collection if not existing"""
        if tasks_col:
            notion_task: CollectionRowBlock = None
            if found_task := _find_resource(self.title, tasks_col):
                logging.warning(f"Task already exists, update its values")
                notion_task = found_task
            else:
                notion_task = tasks_col.add_row(
                    update_views=False)

            for key, value in self.dict_to_insert().items():
                logging.debug(f"{key} -> {value}")

                setattr(notion_task, key, value)

            self._inserted = True

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


def get_tasks(collection: Collection) -> List[Task]:
    """Get rows from collection parsed as Task."""
    tasks: List[Task] = []
    for notion_task in collection.get_rows():
        properties: Dict[str, str] = notion_task.get_all_properties()

        id = notion_task.id
        title = notion_task.title
        task: Task = decode_dsl(id, title, properties)

        tasks.append(task)

    return tasks


def _find_resource(key: str, collection: Collection) -> Optional[CollectionRowBlock]:
    """Find notion CollectionRowBlock resource from collection"""
    resource = None

    key_lowered = key.lower()
    for block in collection.get_rows():
        if hasattr(block, 'title') and block.title.lower().find(key_lowered) > -1:
            resource = block

    return resource
