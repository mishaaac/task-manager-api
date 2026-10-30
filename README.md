# Task Manager API

A practice API built with Python and FastAPI to create, retrieve, update, and delete tasks.
Data is stored in memory and is lost when the server restarts.

## Run locally

Requirements: Python 3.14 or later and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
uv run fastapi dev src/task_manager_api/main.py
```

The API will be available at http://127.0.0.1:8000, with interactive documentation at
http://127.0.0.1:8000/docs.

## Endpoints

| Method | Route | Description |
| --- | --- | --- |
| POST | `/tasks` | Creates a task and returns it with status `201`. |
| GET | `/tasks` | Lists tasks with `count` and `data`. |
| GET | `/tasks?query=bread` | Filters tasks by text contained in the title. |
| GET | `/tasks/{id}` | Retrieves a task. |
| PUT | `/tasks/{id}` | Updates a task's title. |
| DELETE | `/tasks/{id}` | Deletes a task and returns `204` with no response body. |

To create or update a task, send a JSON body:

```json
{
  "title": "Buy bread"
}
```

The title is required, must be a string, and cannot be empty after trimming
leading and trailing whitespace. Invalid input returns `422`; a task that does
not exist returns `404` when the request is otherwise valid.

Search is case-insensitive and trims leading and trailing whitespace.
Omitting `query` or passing an empty or whitespace-only value returns all tasks.

The `task-manager-test-api/` folder includes a Bruno request collection.
Update the example IDs to match tasks created in the current session.
