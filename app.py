import logging
from os import getenv
from typing import *

import schedule
from time import sleep
from dotenv import load_dotenv
from notion.client import NotionClient
from notion.collection import Collection

from lib.jobs import process_inbox_tasks, delete_old_converted_tasks

logger = logging.getLogger(__name__)


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

    # Jobs
    get_block = client.get_block
    process_inbox_tasks(inbox_col, tasks_col, projects_col, get_block)
    schedule.every(2).minutes.do(process_inbox_tasks,
                                 inbox_col, tasks_col, projects_col, get_block)
    schedule.every(1).day.do(delete_old_converted_tasks, inbox_col)

    while True:
        schedule.run_pending()
        sleep(1)
