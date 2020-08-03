# %%
from typing import *
from notion_dsl import decode_dsl
from dotenv import load_dotenv
from notion_api import NotionAPI
from os import getenv

# %%
# Config
load_dotenv()

# %%
token = getenv("NOTION_TOKEN")
notion = NotionAPI(token)
client = notion.client
# TODO: Save in env
inbox_url = 'https://www.notion.so/0fff8abb5b594cb19c0efe7ad2dc5885?v=5c9f252145a94c629c3c778e2f642e23'
tasks_url = 'https://www.notion.so/d16609502fc44cbcb22747c853f549da?v=88db299546b6457fad44eb4ee5ee094b'
projects_url = 'https://www.notion.so/e4f02558ec1442c4a3bb2946e7394d69?v=dc7e8febc0504c818903af092d5c580c'

# %%
inbox_cv = client.get_collection_view(inbox_url)
inbox_tasks = inbox_cv.collection.get_rows()

# %%
tasks = []
for task in inbox_tasks:
    title = task.title
    properties: Dict[str, str] = task.get_all_properties()

    task = decode_dsl(title, properties)

    print(task)
    tasks.append(task)

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