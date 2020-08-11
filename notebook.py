# %%
from typing import *

from notion.block import PageBlock, TextBlock
from notion_dsl import decode_dsl, Task
from dotenv import load_dotenv
from notion.block import PageBlock, TextBlock
from notion.client import NotionClient
from notion.collection import Collection, CollectionRowBlock
from os import getenv

# %%
# Config
load_dotenv()

# %%
token = getenv("NOTION_TOKEN")
client = NotionClient(
    token_v2=token, monitor=True, start_monitoring=True, enable_caching=False)

inbox_url = getenv("INBOX_URL")
tasks_url = getenv("TASKS_URL")
projects_url = getenv("PROJECTS_URL")

# %%
inbox_cv = client.get_collection_view(inbox_url)
inbox_col = inbox_cv.collection

inbox_tasks = inbox_col.get_rows()
tasks = []
for n_task in inbox_tasks:
    properties: Dict[str, str] = n_task.get_all_properties()

    task: Task = decode_dsl(n_task.id, n_task.title, properties)

    print(task)
    tasks.append(task)

# %%
# TODO: Add scheduled tasks to calendar
# TODO: Add laptop tasks to pomodone

# %%
scheduled_view_url = 'https://www.notion.so/d16609502fc44cbcb22747c853f549da?v=02ae4d11fe084753a3320ff1f15e3212'
scheduled_view = client.get_collection_view(scheduled_view_url)

# %%
# Notion changed default_query param name
default_filters = scheduled_view.get('query2')['filter']['filters']
scheduled_view.build_query(filter=default_filters).execute()


# %%
scheduled_view = None
for view in tasks_views:
    name: str = view.name
    print(name)
    if name.lower() == "scheduled":
        scheduled_view = view
# %%
scheduled_collection = scheduled_view.collection

sched_rows = scheduled_collection.get_rows()
# %%
scheduled_tasks = client.filter_tasks_with_schedule()
print(scheduled_tasks)
for task in scheduled_tasks:
    print(task.values)
