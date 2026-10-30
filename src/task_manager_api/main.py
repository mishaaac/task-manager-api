from fastapi import FastAPI, Query, Body, HTTPException

app = FastAPI(title='Task Manager')


class Task:
    id_counter = 1

    def __init__(self, title: str):
        self.id = Task.id_counter
        self.title = title

        Task.id_counter += 1


tasks: list[Task] = []


@app.post('/tasks', status_code=201)
def create_task(raw_task: dict = Body(...)):
    title = validate_title(raw_task)
    task = Task(title)
    tasks.append(task)
    return task


@app.get('/tasks')
def get_tasks(query: str | None = Query(default=None, description='Filter tasks')):
    if query:
        query = query.strip().lower()

    if query:
        filtered_tasks = []
        for task in tasks:
            if query in task.title.lower():
                filtered_tasks.append(task)
        return {'count': len(filtered_tasks), 'data': filtered_tasks}
    return {'count': len(tasks), 'data': tasks}


@app.get('/tasks/{id}')
def get_task(id: int):
    for task in tasks:
        if task.id == id:
            return task

    raise HTTPException(status_code=404, detail='task not found')


@app.put('/tasks/{id}')
def update_task(id: int, raw_task: dict = Body(...)):
    title = validate_title(raw_task)
    for task in tasks:
        if task.id == id:
            task.title = title
            return {'message': 'task updated successfully'}

    raise HTTPException(status_code=404, detail='task not found')


@app.delete('/tasks/{id}', status_code=204)
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task.id == id:
            tasks.pop(index)
            return

    raise HTTPException(status_code=404, detail='task not found')


def validate_title(raw_task: dict):
    if 'title' not in raw_task:
        raise HTTPException(status_code=422, detail='title is mandatory')

    title = raw_task['title']
    if not isinstance(title, str):
        raise HTTPException(status_code=422, detail='title must be a string')

    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail='title cannot be empty')

    return title
