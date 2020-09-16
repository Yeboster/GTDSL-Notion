import logging
from typing import *

from notion.collection import Collection

from .dsl import Task, get_tasks, get_tasks_and_related_projects
from gcalendar.gcalendar import GCalendar

logger = logging.getLogger(__name__)


def process_inbox_tasks(
    inbox_col: Collection,
    tasks_col: Collection,
    projects_col: Collection,
    get_block: Callable,
    gcalendar: GCalendar,
):
    logging.info("--- PROCESSING TASKS ----")
    tasks: List[Task] = get_tasks(inbox_col)
    logging.info(f"List inbox tasks {tasks}")

    for task in tasks:
        if task.convert:
            task.assign_or_create_project_into(projects_col)

            logging.warning(f"Creating new task for {task}")

            notion_task = task.insert_into(tasks_col, gcalendar)
            notion_task.inserted = True
            logging.info(notion_task.get_all_properties())

            logging.debug("Running post creation actions")

            inbox_block = get_block(task.inbox_id)
            logging.info(f"inbox block: {inbox_block}")
            task.post_creation_action(inbox_block)

            logging.warning("Task correctly inserted.")

    logging.info("--- PROCESSING FINISHED ---")


def delete_old_converted_tasks(inbox_col: Collection, get_block: Callable):
    """Delete old converted tasks job"""
    logging.info("--- DELETING TASKS ----")
    tasks: List[Task] = get_tasks(inbox_col)
    for task in tasks:
        if task.can_be_deleted():
            logging.info(f"Removing Task '{task.title}'")
            get_block(task.inbox_id).remove()
    logging.info("--- DELETING TASKS FINISHED ----")


def create_or_update_events(
    collection: Collection, get_block: Callable, gcalendar: GCalendar, days_range: int
):
    """Create or update calendar events on the collection."""
    logging.info("--- PROCESSING EVENTS ----")
    tasks: List[Task] = get_tasks_and_related_projects(collection)
    for task in tasks:
        if not task.inserted and task.scheduled:
            # Check if event already exists
            events = gcalendar.find_events_with(
                summary=task.calendar_title(), not_before_days=days_range
            )
            logging.info(f"task: {task.calendar_title()} events: {events}")
            if events and len(events) > 0:
                for event in events:
                    gcalendar.delete_event(event["id"])

            task.add_to_calendar(gcalendar)

            # TODO: Change name of inbox_id
            get_block(task.inbox_id).inserted = True
    logging.info("--- PROCESSING EVENTS FINISHED ----")
