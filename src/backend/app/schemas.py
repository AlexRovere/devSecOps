""" Pydantic schemas for the Task Manager application."""
from pydantic import BaseModel, Field
from datetime import datetime


class TaskCreate(BaseModel):
    """ Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class TaskUpdate(BaseModel):
    """ Schema for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    status: str | None = Field(default=None, pattern="^(TODO|DOING|DONE)$")


class TaskOut(BaseModel):
    """ Schema for outputting task details."""
    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config(object):
        """ Enable ORM mode to work with SQLAlchemy models."""
        from_attributes = True
