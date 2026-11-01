# Task Manager API

A practice API built with Python and FastAPI to create, retrieve, update, and delete tasks.
The API loads 200 example tasks at startup. Changes are stored in memory and are
lost when the server restarts.

## Run locally

Requirements: Python 3.14 or later and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
uv run fastapi dev src/task_manager_api/main.py
```

The API will be available at http://127.0.0.1:8000, with interactive documentation at
http://127.0.0.1:8000/docs.

## Example tasks

The [tasks.json](src/task_manager_api/tasks.json) file contains 200 task creation
bodies. The API reads this file relative to `main.py`, validates each entry with
`TaskCreateDTO`, and assigns IDs and timestamps when loading it. No manual POST
requests are needed to start exploring the examples.

The examples cover work, study, personal activities, finance, and home tasks,
with all statuses and priorities, ten fictional authors, empty and multiple tags,
optional content, and dates before and after November 1, 2026. Each entry can also
be sent individually to `POST /tasks`.

The original 100 examples are preserved, with 100 additional tasks covering zero
through five tags. There are 50 tasks per status, 50 per priority, and 18 tasks
without tags. The following totals apply immediately after startup:

| Query | Matching tasks |
| --- | --- |
| `/tasks` | 200, including tasks without tags. |
| `/tasks?tag=home` | 98. |
| `/tasks?tag=home&tag=study` | 51. |
| `/tasks?tag=home&tag=study&tag=work` | 30. |
| `/tasks?tag=home&tag=study&tag=work&tag=finance` | 10. |
| `/tasks?tag=home&tag=study&tag=work&tag=finance&tag=personal` | 5. |

For example, add `per_page=50` to the home/study query to get two pages of
matches, or use `per_page=7&page=2` with home/study/work to inspect a middle page.

POST, PUT, PATCH, and DELETE only change the in-memory data; they do not rewrite
the JSON file. Restarting restores the examples. To start with no examples, set
the file contents to `[]`.

## Endpoints

| Method | Route | Description |
| --- | --- | --- |
| POST | `/tasks` | Creates a task and returns it with status `201`. |
| GET | `/tasks` | Returns a paginated object with tasks in `items`. |
| GET | `/tasks?status=pending&priority=high&tag=work` | Filters tasks by status, priority, and tag. |
| GET | `/tasks/{id}` | Retrieves a task. |
| PUT | `/tasks/{id}` | Replaces a task's editable fields and refreshes `updated_at`. |
| PATCH | `/tasks/{id}` | Updates only the submitted task fields and refreshes `updated_at`. |
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

Creating a task requires `title` and `author`; replacing with PUT also requires `status`
and `priority`. Titles and author names must contain 1–100 characters after
trimming whitespace, and the author's email must be valid. Invalid input returns
`422`; a task that does not exist returns `404` when the request is otherwise valid.

Allowed statuses are `pending`, `in_progress`, `completed`, and `canceled`.
Priorities are `low`, `medium`, `high`, and `urgent`. Tags are `work`, `study`,
`personal`, `finance`, and `home`. Query filters are optional and combine with AND.
The query parameter for tags is singular: `tag`. Omit it to include tasks with any
tags, including tasks without tags. Repeat it to require every selected tag:

```text
/tasks
/tasks?tag=home
/tasks?tag=home&tag=study
/tasks?tag=home&tag=study&tag=work
```

For example, `tag=home&tag=study` matches tasks containing both `home` and `study`;
they may also have additional tags. Each value must be one of the allowed tags.

## Pagination, search, and ordering

`GET /tasks` defaults to page 1, ten tasks per page, ordered by ascending ID.
Use `page` (at least 1), `per_page` (1–50), `order_by` (`id` or `title`), and
`direction` (`asc` or `desc`) to change the result:

```text
/tasks?page=2&per_page=10
/tasks?order_by=title&direction=asc&per_page=20
/tasks?search=presupuesto&order_by=title
/tasks?status=pending&priority=high&tag=work
```

`search` matches part of the title without distinguishing uppercase and lowercase.
It accepts 3–50 characters matching the configured word, whitespace, and hyphen
pattern. All filters combine with AND and run before counting and pagination;
ordering also runs before selecting the requested page.

The response includes `page`, `per_page`, `total`, `total_pages`, `has_prev`,
`has_next`, `order_by`, `direction`, `search`, and `items`. Asking for a page beyond
the last one returns the last available page. With no matches, the response has
`page: 1`, `total: 0`, `total_pages: 0`, `items: []`, and both navigation flags false.

## Partial updates

Send only the fields you want to change to `PATCH /tasks/{id}`:

```json
{
  "status": "completed",
  "priority": "high"
}
```

Supported fields are `title`, `content`, `status`, `priority`, `tags`, and
`due_date`. Omitted fields, the author, and `created_at` stay unchanged.
Use `null` to clear `content` or `due_date`, and `[]` to remove all tags.
Explicit `null` is rejected for `title`, `status`, `priority`, and `tags`.
An empty body `{}` preserves all editable fields and refreshes `updated_at`.

The [bruno/](bruno/README.md) folder contains an OpenCollection YAML collection
with 24 ordered requests and automated response checks. Open it in Bruno and run
the full collection, or follow its README to use the CLI. Task IDs are captured
automatically from the creation responses.
