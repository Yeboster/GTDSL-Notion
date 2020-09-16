from dataclasses import dataclass
from datetime import date, datetime, timedelta
import logging
from typing import Any, Dict, List, Optional, Callable

from gcalendar.gcalendar import GCalendar
from notion.block import TextBlock
from notion.collection import Collection, CollectionRowBlock, NotionDate

logger = logging.getLogger(__name__)


@dataclass
class Project:
    """Class to represent notion GTD project"""

    id: str
    title: str


@dataclass
class Task:
    """Stateless class to represent notion GTD task"""

    inbox_id: str
    id: Optional[str] = None
    title: Optional[str] = None
    project_name: Optional[str] = None
    assigned_project: Optional[Project] = None
    url: Optional[str] = None
    status: Optional[str] = None
    context: Optional[str] = None
    scheduled: Optional[NotionDate] = None
    time_repetition: bool = False
    created_at: Optional[datetime] = None
    convert: bool = False
    inserted: bool = False

    def can_be_deleted(self) -> bool:
        delete = False
        if not self.convert and self.inserted:
            if datetime.now() - self.created_at > timedelta(hours=2):
                delete = True

        return delete

    def apply_properties_from(self, properties: Dict[str, str]) -> None:
        keys = [
            "scheduled",
            "status",
            "context",
            "url",
            "created_at",
            "inserted",
            # Inbox collection specific
            "convert",
            "time_repetition",
            # Tasks collection specific
            "project",
        ]
        for key in keys:
            try:
                value = properties[key]
                setattr(self, key, value)
            except:
                # There are some keys present only in inbox coll
                pass

    def dict_to_insert(self) -> Dict[str, Any]:
        keys = ["title", "project", "scheduled", "url", "status", "context", "inserted"]
        insert_dict: Dict[str, Any] = {}
        for key in keys:
            if key == "project":
                if prj := self.assigned_project:
                    insert_dict["project"] = prj.id
            else:
                insert_dict[key] = getattr(self, key)

        return insert_dict

    def assign_or_create_project_into(self, projects_col: Collection) -> None:
        """Get project based on name. If found it returns a Project GTD wrapper"""
        if self.project_name and projects_col and not self.assigned_project:

            project: Optional[Project] = None
            if found_project := _find_resource(self.project_name, projects_col):
                project = Project(found_project.id, found_project.title)

            if project is None:
                logging.warning(
                    f"Create project '{self.project_name}' since no one found."
                )
                notion_project: CollectionRowBlock = projects_col.add_row(
                    update_views=False
                )
                notion_project.title = self.project_name
                notion_project.stage = "💡Idea"

                project = Project(notion_project.id, notion_project.title)

            self.assigned_project = project

    def insert_into(self, tasks_col: Collection, gcalendar: GCalendar) -> None:
        """Insert task into collection if not existing"""
        if tasks_col and self.title:
            notion_task: Optional[CollectionRowBlock] = None
            if found_task := _find_resource(self.title, tasks_col):
                logging.warning(f"Task already exists, update its values")
                notion_task = found_task
            else:
                notion_task = tasks_col.add_row(update_views=False)

            self.id = notion_task.id
            for key, value in self.dict_to_insert().items():
                logging.debug(f"{key} -> {value}")

                if key == "scheduled":
                    self.add_to_calendar(gcalendar)

                # TODO: Improve
                self.inserted = True
                setattr(notion_task, key, value)

    def calendar_title(self):
        title = (
            self.assigned_project.title + ": " if self.assigned_project else ""
        ) + self.title
        return title

    def add_to_calendar(self, gcalendar):
        if notion_date := self.scheduled:
            insert_fun = (
                gcalendar.insert_time_repetition_event
                if self.time_repetition
                else gcalendar.insert_event
            )

            start_date = notion_date.start
            end_date = notion_date.end

            logging.info("Adding task to Calendar")

            insert_fun(self.calendar_title(), start_date=start_date, end_date=end_date)

    def post_creation_action(self, inbox_block: CollectionRowBlock) -> None:
        """Actions after creating GTD task."""
        inbox_block.convert = False
        inbox_block.inserted = True
        content = (
            f"Added task to **'{self.assigned_project.title}'** project."
            if self.assigned_project
            else f"Task added without project."
        )
        inbox_block.children.add_new(TextBlock, title=content)
        # TODO: Add link to page


def decode_dsl(id: str, content: str, properties: Dict[str, str]) -> Task:
    task: Task = Task(id)
    if (pos := content.find(":")) > -1:
        task.title = content[pos + 1 :].strip().capitalize()
        task.project_name = content[:pos].strip().capitalize()
    else:
        task.title = content.strip().capitalize()

    task.apply_properties_from(properties)

    return task


def get_tasks_and_related_projects(collection: Collection) -> List[Task]:
    """Get rows from tasks collection parsed as Task."""
    tasks: List[Task] = []
    for notion_task in collection.get_rows():
        properties: Dict[str, str] = notion_task.get_all_properties()

        id = notion_task.id
        title = notion_task.title
        task: Task = decode_dsl(id, title, properties)

        if "project" in properties:
            project_list: List[CollectionRowBlock] = properties["project"]
            if len(project_list) > 0 and (first := project_list[0]):
                project: Project = Project(first.id, first.title)
                task.assigned_project = project

        tasks.append(task)

    return tasks


def get_tasks(collection: Collection) -> List[Task]:
    """Get rows from collection parsed as Task."""
    tasks: List[Task] = []
    for notion_task in collection.get_rows():
        properties: Dict[str, str] = notion_task.get_all_properties()

        id = notion_task.id
        title = notion_task.title
        task: Task = decode_dsl(id, title, properties)

        tasks.append(task)

    return tasks


def _find_resource(key: str, collection: Collection) -> Optional[CollectionRowBlock]:
    """Find notion CollectionRowBlock resource from collection"""
    resource = None

    key_lowered = key.lower()
    for block in collection.get_rows():
        if hasattr(block, "title") and block.title.lower().find(key_lowered) > -1:
            resource = block
            break

    return resource
