# %%
from pprint import pprint
from typing import *

from notion.block import PageBlock, TextBlock
from dsl import decode_dsl, Task
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
    token_v2=token, monitor=True, start_monitoring=True, enable_caching=False
)

inbox_url = getenv("INBOX_URL")
tasks_url = getenv("TASKS_URL")
projects_url = getenv("PROJECTS_URL")

# %%
inbox_cv = client.get_collection_view(inbox_url)
inbox_col = inbox_cv.collection
inbox_tasks = inbox_col.get_rows()


# %%
tasks = []
for n_task in inbox_tasks:
    properties: Dict[str, str] = n_task.get_all_properties()

    task: Task = decode_dsl(n_task.id, n_task.title, properties)

    print(task)
    tasks.append(task)

# %%


def callback(record, difference):
    print(record, difference)


inbox_col.add_callback(callback)

while True:
    pass
