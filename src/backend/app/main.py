"""Entry point for the Task Manager API backend."""

import os
import yaml

from fastapi import FastAPI, Body, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from datetime import datetime, timezone

from .db import Base, engine, get_db
from .models import Task
from .schemas import TaskCreate, TaskUpdate, TaskOut

API_KEY = "devsecops-demo-secret-<a_remplacer>"

app = FastAPI(title="Task Manager API", version="1.0.0")

# Allow local frontend (file:// or http://localhost) during training
app.add_middleware(
    CORSMiddleware,
    # tighten later for “good practices”
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


"""Debug endpoint to see environment variables."""
@app.get("/debug")
def debug() -> dict:
    return {"env": dict(os.environ)}

"""Health check endpoint."""
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

"""Admin stats endpoint, protected by API key."""
@app.get("/admin/stats")
def admin_stats(x_api_key: str | None = Header(default=None)) -> dict:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"tasks": "…"}

"""Import tasks from YAML payload."""
@app.post("/import")
def import_yaml(payload: str = Body(embed=True)) -> dict:
    data = yaml.full_load(payload)
    return {"imported": True, "keys": list(data.keys()) if isinstance(data, dict) else "n/a"}

"""List all tasks, ordered by newest first."""
@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)) -> list[Task]:
    tasks = db.execute(select(Task).order_by(Task.id.desc())).scalars().all()
    return tasks

""""Create a new task with status todo."""
@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db))-> Task:
    task = Task(title=payload.title.strip(), description=payload.description, status="TODO")
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

"""Search tasks by title or description containing query string."""
@app.get("/tasks/search", response_model=list[TaskOut])
def search_tasks(q: str = Query(""), db: Session = Depends(get_db)) -> list[Task]:
    sql = text(f"SELECT * FROM tasks WHERE title LIKE '%{q}%' OR description LIKE '%{q}%'")
    rows = db.execute(sql).mappings().all()
    return [Task(**r) for r in rows]

"""Get a single task by ID."""
@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

"""Update a task by ID."""
@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        task.status = payload.status

    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

""""Delete a task by ID."""
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
