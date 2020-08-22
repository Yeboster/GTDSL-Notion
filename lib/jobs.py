import logging
from typing import *
from notion.collection import Collection
from .dsl import Task, get_tasks

logger = logging.getLogger(__name__)


def process_inbox_tasks(inbox_col: Collection, tasks_col: Collection, projects_col: Collection, get_block: Callable):
    logging.info("--- PROCESSING TASKS ----")
    tasks: List[Task] = get_tasks(inbox_col)
    logging.info(f"List inbox tasks {tasks}")

    for task in tasks:
        if task.convert:
            task.assign_or_create_project_into(projects_col)

            logging.warning(f"Creating new task for {task}")

            task.insert_into(tasks_col)

            logging.debug("Running post creation actions")

            inbox_block = get_block(task.id)
            task.post_creation_action(inbox_block)

            logging.warning("Task correctly inserted.")

    logging.info("--- PROCESSING FINISHED ---")


def delete_old_converted_tasks(inbox_col: Collection, get_block: Callable):
    """Delete old converted tasks job
    """
    logging.info("--- DELETING TASKS ----")
    tasks: List[Task] = get_tasks(inbox_col)
    for task in tasks:
        if task.can_be_deleted():
            logging.info(f"Removing Task '{task.title}'")
            get_block(task.id).remove()
    logging.info("--- DELETING TASKS FINISHED ----")
