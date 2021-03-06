import logging
from os import getenv
from typing import *

import schedule
from time import sleep
from dotenv import load_dotenv
from notion.client import NotionClient
from notion.collection import Collection

from gtdsl.jobs import process_inbox_tasks, delete_old_converted_tasks
from gcalendar.gcalendar import GCalendar

logger = logging.getLogger(__name__)


def setup():
    load_dotenv()

    log_level = (
        logging.INFO
        if getenv("ENVIRONMENT", "development") == "development"
        else logging.WARN
    )
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=log_level
    )

    token = getenv("NOTION_TOKEN")
    inbox_url = getenv("INBOX_URL")
    tasks_url = getenv("TASKS_URL")
    projects_url = getenv("PROJECTS_URL")
    calendar_id = getenv("GCALENDAR_ID")
    timezone = getenv("GTIMEZONE")

    token_pickle_path = getenv("GTOKEN_PICKLE_PATH")
    gcredentials_path = getenv("GCREDENTIALS_PATH")

    if not (
        token
        and inbox_url
        and tasks_url
        and projects_url
        and calendar_id
        and token_pickle_path
        and gcredentials_path
    ):
        raise Exception("Missing envs.")

    client = NotionClient(
        token_v2=token, monitor=True, start_monitoring=True, enable_caching=False
    )

    logging.info("Starting the application...")

    inbox_cv = client.get_collection_view(inbox_url)
    inbox_col: Collection = inbox_cv.collection
    projects_cv = client.get_collection_view(projects_url)
    projects_col: Collection = projects_cv.collection
    tasks_cv = client.get_collection_view(tasks_url)
    tasks_col: Collection = tasks_cv.collection

    get_block = client.get_block

    calendar = GCalendar(
        calendar_id=calendar_id, credentials_path=gcredentials_path, pickle_path=token_pickle_path, timezone=timezone
    )

    return inbox_col, projects_col, tasks_col, get_block, calendar


if __name__ == "__main__":
    inbox_col, projects_col, tasks_col, get_block, calendar = setup()

    # Run once
    process_inbox_tasks(inbox_col, tasks_col, projects_col, get_block, calendar)
    delete_old_converted_tasks(inbox_col, get_block)

    # Jobs
    schedule.every(10).minutes.do(
        process_inbox_tasks, inbox_col, tasks_col, projects_col, get_block, calendar
    )
    schedule.every(2).hours.do(delete_old_converted_tasks, inbox_col, get_block)

    while True:
        schedule.run_pending()
        sleep(1)
