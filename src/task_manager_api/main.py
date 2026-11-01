from datetime import datetime
from enum import Enum
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator

app = FastAPI(title='Task Manager')

# ================================================================
#                       ENUMS
# ================================================================


class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELED = 'canceled'


class TaskPriority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'


class AllowedTags(str, Enum):
    WORK = 'work'
    STUDY = 'study'
    PERSONAL = 'personal'
    FINANCE = 'finance'
    HOME = 'home'


# ================================================================
#                       MODELS (ENTIDADES PURAS)
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
        author: Author
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

    @field_validator('title', 'status', 'priority', 'tags', mode='before')
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError('field cannot be null')
        return value


class TaskResponseDTO(TaskBaseDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ================================================================
#                       ENDPOINTS
# ================================================================


@app.get('/')
def home():
    return {'message': 'Welcome to Task Manager'}


@app.post('/tasks', response_model=TaskResponseDTO, status_code=201)
def create_task(new_task: TaskCreateDTO):
    author_entity = Author(
        name=new_task.author.name,
        email=new_task.author.email
    )

    task = Task(
        title=new_task.title,
        content=new_task.content,
        status=new_task.status,
        priority=new_task.priority,
        tags=new_task.tags,
        due_date=new_task.due_date,
        author=author_entity
    )

    tasks.append(task)

    return task


@app.get('/tasks', response_model=list[TaskResponseDTO], status_code=200)
def get_tasks(
    status: TaskStatus | None = Query(
        default=None, description="Filter by status"),
    priority: TaskPriority | None = Query(
        default=None, description="Filter by priority"),
    tag: AllowedTags | None = Query(default=None, description="Filter by tags")
):
    filtered_tasks = tasks

    if status:
        filtered_tasks = [
            task for task in filtered_tasks if task.status == status]

    if priority:
        filtered_tasks = [
            task for task in filtered_tasks if task.priority == priority]

    if tag:
        filtered_tasks = [task for task in filtered_tasks if tag in task.tags]

    return filtered_tasks


@app.get('/tasks/{id}', response_model=TaskResponseDTO, status_code=200)
def get_task(id: int):
    for task in tasks:
        if task.id == id:
            return task

    raise HTTPException(status_code=404, detail=f'task ({id}) not found')


@app.put('/tasks/{id}', response_model=TaskResponseDTO, status_code=200)
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

    raise HTTPException(status_code=404, detail=f'task ({id}) not found')


@app.patch('/tasks/{id}', response_model=TaskResponseDTO, status_code=200)
def patch_task(id: int, partial_task: TaskPatchDTO):
    for task in tasks:
        if task.id == id:
            update_data = partial_task.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(task, key, value)

            task.updated_at = datetime.now()

            return task

    raise HTTPException(status_code=404, detail=f'task ({id}) not found')


@app.delete('/tasks/{id}', status_code=204)
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task.id == id:
            tasks.pop(index)
            return

    raise HTTPException(status_code=404, detail=f'task ({id}) not found')
