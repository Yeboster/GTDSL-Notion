from typing import *
from dotenv import load_dotenv
from notion_api import NotionAPI
from os import getenv


if __name__ == '__main__':
    # Config
    load_dotenv()

    token = getenv("NOTION_TOKEN")
    client = NotionAPI(token)
    tasks = client.get_tasks()
    print(tasks)
    print(tasks.children)
    # TODO:
    # x- Take all pages
    # x- Find the tasks one
    # - List of collections
    # - Use view next actions
    # - Get list of all tasks
    # - Add task in collection tasks
    # - Polling if there are more tasks: use sorted created_at view
    # - Add into db
