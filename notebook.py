# %%
from typing import *

from notion.block import PageBlock, TextBlock
from notion_dsl import TO_INSERT_KEYS, decode_dsl, Task
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

# TODO: Save in env
inbox_url = 'https://www.notion.so/0fff8abb5b594cb19c0efe7ad2dc5885?v=5c9f252145a94c629c3c778e2f642e23'
tasks_url = 'https://www.notion.so/d16609502fc44cbcb22747c853f549da?v=88db299546b6457fad44eb4ee5ee094b'
projects_url = 'https://www.notion.so/e4f02558ec1442c4a3bb2946e7394d69?v=dc7e8febc0504c818903af092d5c580c'

# %%
inbox_cv = client.get_collection_view(inbox_url)
inbox_col = inbox_cv.collection

# %%
inbox_tasks = inbox_col.get_rows()
tasks = []
for n_task in inbox_tasks:
    properties: Dict[str, str] = n_task.get_all_properties()

    task: Task = decode_dsl(n_task.id, n_task.title, properties)

    print(task)
    tasks.append(task)

# %%
# Find id of Project or create new one
task: Task = tasks[0]  # Pass as param
# TODO: Project is optional
project_task = task.project.lower()

projects_cv = client.get_collection_view(projects_url)
projects_col: Collection = projects_cv.collection
projects_schema = projects_col.get_schema_properties()

found_project: CollectionRowBlock = None
for project in projects_col.get_rows():
    title: str = project.title
    if title and title.lower().find(project_task) > -1:
        print(project)
        found_project = project
        break

project_to_link: CollectionRowBlock = found_project
if found_project is None:
    project_to_link: CollectionRowBlock = projects_col.add_row()
    # Hard coding values, for now
    project_to_link.title = project_task.capitalize()
    project_to_link.stage = '💡Idea'
    # TODO: Add other properties like: tags, location, ...

# %%
# Create task and link it to project, if any
tasks_cv = client.get_collection_view(tasks_url)
tasks_col: Collection = tasks_cv.collection
tasks_schema = tasks_col.get_schema_properties()
if task.convert:
   # update_views=False improves performance
    created_task: CollectionRowBlock = tasks_col.add_row(update_views=False)
    for key in TO_INSERT_KEYS:
        if key == "project" and project_to_link:
            value = project_to_link.id
        else:
            value = getattr(task, key)

        print(key, value)

        setattr(created_task, key, value)
    # Post creation
    inbox_task: CollectionRowBlock = client.get_block(task.id)
    inbox_task.convert = False
    task_title = inbox_task.title
    inbox_task.title = "✅ " + task_title
    content = f"Added task to **'{task.project}'** project" if task.project else f"Task added without project"
    inbox_task.children.add_new(TextBlock, title=content)

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
