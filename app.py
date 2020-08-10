import logging
from os import getenv
from typing import *

from dotenv import load_dotenv
from notion.client import NotionClient
from notion.collection import Collection

from notion_dsl import Task, decode_dsl

logger = logging.getLogger(__name__)


def get_tasks(collection: Collection) -> List[Task]:
    tasks: List[Task] = []
    for notion_task in collection.get_rows():
        properties: Dict[str, str] = notion_task.get_all_properties()

        id = notion_task.id
        title = notion_task.title
        task: Task = decode_dsl(id, title, properties)

        logger.debug(task)

        tasks.append(task)

    return tasks


if __name__ == '__main__':
    # Setup
    load_dotenv()
    log_level = logging.DEBUG if getenv(
        'ENVIRONMENT', 'development') == 'development' else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=log_level)

    token = getenv("NOTION_TOKEN")
    client = NotionClient(
        token_v2=token, monitor=True, start_monitoring=True, enable_caching=False)

    inbox_url = getenv("INBOX_URL")
    tasks_url = getenv("TASKS_URL")
    projects_url = getenv("PROJECTS_URL")

    inbox_cv = client.get_collection_view(inbox_url)
    inbox_col = inbox_cv.collection

    tasks = get_tasks(inbox_col)
