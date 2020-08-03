from typing import *
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    """Class to represent notion GTD tasks"""
    name: str = None
    project: str = None
    scheduled: datetime = None
    type: str = None
    context: str = None

def extract_properties(properties: Dict[str, str], task: Task) -> Task:
    keys = ['scheduled', 'type', 'context']
    for key in keys:
        value = properties[key]
        if key == 'scheduled' and value is not None:
            # TODO: Add also end
            setattr(task, key, value.start)
        else:
            setattr(task, key, value)

    return task

def decode_dsl(content: str, properties: Dict[str, str]) -> Task:
    task: Task = Task()
    if (pos := content.find(':')) > -1:
        task.name = content[pos+1:].strip()
        task.project = content[:pos].strip()
    else:
        task.name = content.strip()

    task = extract_properties(properties, task)
    
    return task