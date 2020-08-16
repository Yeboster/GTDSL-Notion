import logging
from os import getenv
from typing import *

import schedule
from time import sleep
from dotenv import load_dotenv
from notion.client import NotionClient
from notion.collection import Collection

from lib.dsl import Task, get_tasks

logger = logging.getLogger(__name__)


def process_inbox_tasks(inbox_col: Collection, tasks_col: Collection, projects_col: Collection):
    logging.info("--- PROCESSING TASKS ----")
    tasks: List[Task] = get_tasks(inbox_col)
    logging.info(f"List inbox tasks {tasks}")

    for task in tasks:
        if task.convert:
            task.assign_or_create_project_into(projects_col)

            logging.warning(f"Creating new task for {task}")

            task.insert_into(tasks_col)

            logging.debug("Running post creation actions")

            inbox_block = client.get_block(task.id)
            task.post_creation_action(inbox_block)

            logging.warning("Task correctly inserted.")

    logging.info("--- PROCESSING FINISHED ---")


if __name__ == '__main__':
    # Setup
    load_dotenv()

    log_level = logging.INFO if getenv(
        'ENVIRONMENT', 'development') == 'development' else logging.WARN
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=log_level)

    token = getenv("NOTION_TOKEN")
    inbox_url = getenv("INBOX_URL")
    tasks_url = getenv("TASKS_URL")
    projects_url = getenv("PROJECTS_URL")

    if not (token and inbox_url and tasks_url and projects_url):
        raise Exception("Missing envs.")

    client = NotionClient(
        token_v2=token, monitor=True, start_monitoring=True, enable_caching=False)

    logging.info("Starting the application...")

    inbox_cv = client.get_collection_view(inbox_url)
    inbox_col = inbox_cv.collection
    projects_cv = client.get_collection_view(projects_url)
    projects_col: Collection = projects_cv.collection
    tasks_cv = client.get_collection_view(tasks_url)
    tasks_col: Collection = tasks_cv.collection

    process_inbox_tasks(inbox_col, tasks_col, projects_col)
    schedule.every(1).minutes.do(process_inbox_tasks,
                                 inbox_col, tasks_col, projects_col)

    while True:
        schedule.run_pending()
        sleep(1)
