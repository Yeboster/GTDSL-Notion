import logging
from time import sleep
from typing import *

import schedule

from gtdsl.jobs import (
    create_or_update_events,
    delete_old_converted_tasks,
    process_inbox_tasks,
)
from settings import setup

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    inbox_col, projects_col, tasks_col, get_block, calendar, days_range = setup()

    # Run once
    create_or_update_events(tasks_col, get_block, calendar, days_range)
    process_inbox_tasks(inbox_col, tasks_col, projects_col, get_block, calendar)
    delete_old_converted_tasks(inbox_col, get_block)

    # Jobs
    schedule.every(10).minutes.do(
        process_inbox_tasks, inbox_col, tasks_col, projects_col, get_block, calendar
    )
    schedule.every(30).minutes.do(
        create_or_update_events, tasks_col, get_block, calendar, days_range
    )
    schedule.every(2).hours.do(delete_old_converted_tasks, inbox_col, get_block)

    while True:
        schedule.run_pending()
        sleep(1)
