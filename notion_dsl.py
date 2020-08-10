from typing import *
from dataclasses import dataclass
from notion.collection import NotionDate


TO_INSERT_KEYS: List[str] = ['title',
                             'project', 'scheduled', 'status', 'context']


@dataclass
class Task:
    """Class to represent notion GTD tasks"""
    id: str = None
    title: str = None
    project: str = None
    scheduled: NotionDate = None
    status: str = None
    context: str = None
    convert: bool = False


def extract_properties(properties: Dict[str, str], task: Task) -> Task:
    keys = ['scheduled', 'status', 'context', 'convert']
    for key in keys:
        value = properties[key]
        setattr(task, key, value)

    return task


def decode_dsl(id: str, content: str, properties: Dict[str, str]) -> Task:
    task: Task = Task()
    task.id = id
    if (pos := content.find(':')) > -1:
        task.title = content[pos+1:].strip().capitalize()
        task.project = content[:pos].strip().capitalize()
    else:
        task.title = content.strip().capitalize()

    task = extract_properties(properties, task)

    return task
