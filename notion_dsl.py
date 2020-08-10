from typing import *
from dataclasses import dataclass
from notion.collection import NotionDate


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
    project_name: str = None
    choosen_project: Project = None
    scheduled: NotionDate = None
    status: str = None
    context: str = None
    convert: bool = False

    def apply_properties_from(self, properties: Dict[str, str]) -> None:
        keys = ['scheduled', 'status', 'context', 'convert']
        for key in keys:
            value = properties[key]
            setattr(self, key, value)

    def dict_to_insert(self) -> Dict[str, Any]:
        keys = ['title', 'project', 'scheduled', 'status', 'context']
        insert_dict: Dict[str, Any] = {}
        for key in keys:
            if key == 'project':
                if prj := self.choosen_project:
                    insert_dict['project'] = prj.id
            else:
                insert_dict[key] = getattr(self, key)

        return insert_dict


def decode_dsl(id: str, content: str, properties: Dict[str, str]) -> Task:
    task: Task = Task(id)
    if (pos := content.find(':')) > -1:
        task.title = content[pos+1:].strip().capitalize()
        task.project_name = content[:pos].strip().capitalize()
    else:
        task.title = content.strip().capitalize()

    task.apply_properties_from(properties)

    return task
