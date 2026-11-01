# Task Manager API tests with Bruno

This collection uses Bruno's OpenCollection YAML format. It includes 24 ordered
requests and automated checks for HTTP status codes, response data, filters,
timestamps, author validation, partial updates, and deletion. Request names, test labels, and
documentation are in English; sample user input is in Spanish.

## Run in Bruno

1. Start the server from the project root:

   ```bash
   uv run fastapi dev src/task_manager_api/main.py
   ```

2. In Bruno, use **Open Collection** and select the `bruno/` folder.
   If you previously opened `task-manager-test-api/`, open the new location.
3. The collection variable `base_url` points to `http://127.0.0.1:8000`.
   You can change it in the collection variables.
4. Open **Collection Runner** and run all 24 requests in order, in a single run.
   You can also send them manually in that order.
5. Review the results in **Tests**. Status codes `422` and `404` are expected
   responses: their checks should pass.

Start with a freshly launched server and the bundled 200-task example file.
Listing checks read the paginated `items` field. Cases 04–06 use descending ID
order to include the tasks just created. The case with no matches uses a search
string absent from the examples and test tasks. Cases 20–24 cover omitted tags,
one tag, multiple tags, pagination after filtering, and invalid tag values.

## Included cases

| Order | File | Operation | Expected result |
| --- | --- | --- | --- |
| 01 | `01_create_task.yml` | POST `/tasks` | `201`: pending/high task with work and finance tags. |
| 02 | `02_create_second_task.yml` | POST `/tasks` | `201`: in_progress/low task with study and personal tags. |
| 03 | `03_create_task_invalid_email.yml` | POST `/tasks` | `422`: error at `body.author.email`; task is not saved. |
| 04 | `04_get_tasks.yml` | GET with descending ID order and 50 items per page | `200`: page containing both valid tasks in `items`. |
| 05 | `05_filter_first_task.yml` | GET with pending/high and repeated work/finance tags | `200`: includes the first task; every item has both tags. |
| 06 | `06_filter_second_task.yml` | GET with in_progress/low and repeated study/personal tags | `200`: includes the second task; every item has both tags. |
| 07 | `07_filter_no_matches.yml` | GET with pending/low/work and unmatched search | `200`: empty page with `total: 0` and `items: []`. |
| 08 | `08_get_task.yml` | GET `/tasks/{{task1_id}}` | `200`: first task object. |
| 09 | `09_update_task.yml` | PUT `/tasks/{{task1_id}}` | `200`: completed/urgent with a refreshed `updated_at`. |
| 10 | `10_delete_task.yml` | DELETE `/tasks/{{task2_id}}` | `204`: empty body. |
| 11 | `11_get_deleted_task.yml` | GET `/tasks/{{task2_id}}` | `404`: `{"detail":"task (<id>) not found"}`. |
| 12 | `12_patch_task.yml` | PATCH task | Partially update first task. |
| 13 | `13_patch_clear_fields.yml` | PATCH task | Clear nullable fields. |
| 14 | `14_patch_empty.yml` | PATCH task | Patch with an empty object. |
| 15 | `15_patch_invalid_title.yml` | PATCH task | Reject a blank title. |
| 16 | `16_patch_invalid_enums.yml` | PATCH task | Reject invalid enum values. |
| 17 | `17_patch_null_required_fields.yml` | PATCH task | Reject null for nonnullable fields. |
| 18 | `18_patch_missing_task.yml` | PATCH task | Patch a deleted task. |
| 19 | `19_get_task_after_patches.yml` | GET task | Verify persisted patches and rejected input. |
| 20 | `20_list_without_tag_filter.yml` | GET without `tag` | `200`: includes tasks with and without tags. |
| 21 | `21_filter_home.yml` | GET with `tag=home` | `200`: 98 matches, including tasks with additional tags. |
| 22 | `22_filter_home_study.yml` | GET with home/study and 50 items per page | `200`: 51 matches across two pages; every item has both tags. |
| 23 | `23_filter_home_study_work.yml` | GET with home/study/work, page 2 and 7 items per page | `200`: 30 matches across five pages; every item has all three tags. |
| 24 | `24_filter_invalid_tag.yml` | GET with home and an invalid second tag | `422`: validation error at `query.tag.1`. |

The first two requests save `task1_id`, `task2_id`, and response snapshots as
runtime variables. You do not need to edit IDs: they will be 201 and 202 with the
200 startup examples. If you restart the server, run the collection again from
the beginning.

After the run, the first task has the patched title, status, and priority, with empty
tags and cleared content and due date. The second task is deleted. Rejected patches
leave the stored task unchanged.
The server generates timestamps, which are not compared against fixed values.
The PUT request sends the complete body to preserve content, tags, due date,
and author.

## Run from the terminal

With Node.js/npm available and the server running, start from the project root:

```bash
cd bruno
npx --yes @usebruno/cli@4.3.0 run --bail
```

To test another address without editing the collection:

```bash
npx --yes @usebruno/cli@4.3.0 run --bail --env-var base_url=http://127.0.0.1:8001
```

The CLI returns a nonzero exit code if a check fails.
