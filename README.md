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
| GET | `/tasks` | Returns an array of tasks. |
| GET | `/tasks?status=pending&priority=high&tag=work` | Filters tasks by status, priority, and tag. |
| GET | `/tasks/{id}` | Retrieves a task. |
| PUT | `/tasks/{id}` | Replaces a task's editable fields and refreshes `updated_at`. |
| DELETE | `/tasks/{id}` | Deletes a task and returns `204` with no response body. |

To create or update a task, send a JSON body:

```json
{
  "title": "Comprar pan",
  "content": "Visitar la panadería",
  "status": "pending",
  "priority": "medium",
  "tags": ["personal", "home"],
  "due_date": "2026-12-11T12:00:00",
  "author": {
    "name": "Ana",
    "email": "ana@example.com"
  }
}
```

Creating a task requires `title` and `author`; updating also requires `status`
and `priority`. Titles and author names must contain 1–100 characters after
trimming whitespace, and the author's email must be valid. Invalid input returns
`422`; a task that does not exist returns `404` when the request is otherwise valid.

Allowed statuses are `pending`, `in_progress`, `completed`, and `canceled`.
Priorities are `low`, `medium`, `high`, and `urgent`. Tags are `work`, `study`,
`personal`, `finance`, and `home`. Query filters are optional and combine with AND;
the query parameter for tags is singular: `tag`.

The [bruno/](bruno/README.md) folder contains an OpenCollection YAML collection
with 11 ordered requests and automated response checks. Open it in Bruno and run
the full collection, or follow its README to use the CLI. Task IDs are captured
automatically from the creation responses.
