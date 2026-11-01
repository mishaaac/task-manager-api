import json
from datetime import datetime
from enum import Enum
from math import ceil
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

app = FastAPI(title="Task Manager")

# ================================================================
#                           ENUMS
# ================================================================


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AllowedTags(str, Enum):
    WORK = "work"
    STUDY = "study"
    PERSONAL = "personal"
    FINANCE = "finance"
    HOME = "home"


# ================================================================
#                           MODELS
# ================================================================


class Author:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class Task:
    id_counter = 1

    def __init__(
        self,
        title: str,
        content: str | None,
        status: TaskStatus,
        priority: TaskPriority,
        tags: list[AllowedTags],
        due_date: datetime | None,
        author: Author,
    ):
        self.id = Task.id_counter
        self.title = title
        self.content = content
        self.status = status
        self.priority = priority
        self.tags = tags
        self.due_date = due_date
        self.author = author
        self.created_at = datetime.now()
        self.updated_at = self.created_at

        Task.id_counter += 1


tasks: list[Task] = []


# ================================================================
#                       DTOs (PYDANTIC)
# ================================================================


class AuthorDTO(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class TaskBaseDTO(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=100)
    content: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[AllowedTags] = []
    due_date: datetime | None = None
    author: AuthorDTO


class TaskCreateDTO(TaskBaseDTO):
    pass


class TaskUpdateDTO(TaskBaseDTO):
    status: TaskStatus
    priority: TaskPriority


class TaskPatchDTO(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    tags: list[AllowedTags] | None = None
    due_date: datetime | None = None

    @field_validator("title", "status", "priority", "tags", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("field cannot be null")
        return value


class TaskResponseDTO(TaskBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedTaskDTO(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: str | None
    items: list[TaskResponseDTO]


# ================================================================
#                       ENDPOINTS
# ================================================================


@app.get("/")
def home():
    return {"message": "Welcome to Task Manager"}


@app.post("/tasks", response_model=TaskResponseDTO, status_code=201)
def create_task(new_task: TaskCreateDTO):
    author_entity = Author(name=new_task.author.name, email=new_task.author.email)

    task = Task(
        title=new_task.title,
        content=new_task.content,
        status=new_task.status,
        priority=new_task.priority,
        tags=new_task.tags,
        due_date=new_task.due_date,
        author=author_entity,
    )

    tasks.append(task)

    return task


@app.get("/tasks", response_model=PaginatedTaskDTO, status_code=200)
def get_tasks(
    search: str | None = Query(
        None,
        description="Search by title",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$",
    ),
    status: TaskStatus | None = Query(default=None, description="Filter by status"),
    priority: TaskPriority | None = Query(
        default=None, description="Filter by priority"
    ),
    tag: list[AllowedTags] | None = Query(
        default=None,
        description="Require all selected tags. Repeat tag to select multiple values.",
    ),
    per_page: int = Query(10, ge=1, le=50, description="Number of tasks to show"),
    page: int = Query(1, ge=1, description="Number of page"),
    order_by: Literal["id", "title"] = Query("id", description="Field order"),
    direction: Literal["asc", "desc"] = Query("asc", description="Order"),
):
    filtered_tasks = tasks

    if search:
        filtered_tasks = [
            task for task in filtered_tasks if search.lower() in task.title.lower()
        ]

    if status:
        filtered_tasks = [task for task in filtered_tasks if task.status == status]

    if priority:
        filtered_tasks = [task for task in filtered_tasks if task.priority == priority]

    if tag:
        filtered_tasks = [
            task
            for task in filtered_tasks
            if all(selected_tag in task.tags for selected_tag in tag)
        ]

    total = len(filtered_tasks)

    total_pages = ceil(total / per_page) if total > 0 else 0

    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages)

    filtered_tasks = sorted(
        filtered_tasks,
        key=lambda task: getattr(task, order_by),
        reverse=(direction == "desc"),
    )

    if total_pages == 0:
        items = []
    else:
        start = (current_page - 1) * per_page
        items = filtered_tasks[start : start + per_page]

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedTaskDTO(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=search,
        items=items,
    )


@app.get("/tasks/{id}", response_model=TaskResponseDTO, status_code=200)
def get_task(id: int):
    for task in tasks:
        if task.id == id:
            return task

    raise HTTPException(status_code=404, detail=f"task ({id}) not found")


@app.put("/tasks/{id}", response_model=TaskResponseDTO, status_code=200)
def update_task(id: int, updated_task: TaskUpdateDTO):
    for task in tasks:
        if task.id == id:
            task.title = updated_task.title
            task.content = updated_task.content
            task.status = updated_task.status
            task.priority = updated_task.priority
            task.tags = updated_task.tags
            task.due_date = updated_task.due_date

            task.author.name = updated_task.author.name
            task.author.email = updated_task.author.email

            task.updated_at = datetime.now()

            return task

    raise HTTPException(status_code=404, detail=f"task ({id}) not found")


@app.patch("/tasks/{id}", response_model=TaskResponseDTO, status_code=200)
def patch_task(id: int, partial_task: TaskPatchDTO):
    for task in tasks:
        if task.id == id:
            update_data = partial_task.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(task, key, value)

            task.updated_at = datetime.now()

            return task

    raise HTTPException(status_code=404, detail=f"task ({id}) not found")


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task.id == id:
            tasks.pop(index)
            return

    raise HTTPException(status_code=404, detail=f"task ({id}) not found")


# ================================================================
#                       EXAMPLE DATA
# ================================================================

# Loaded at startup; API changes are only stored in memory.
tasks_path = Path(__file__).with_name("tasks.json")

if tasks_path.exists():
    with tasks_path.open(encoding="utf-8") as tasks_file:
        for task_data in json.load(tasks_file):
            create_task(TaskCreateDTO.model_validate(task_data))
