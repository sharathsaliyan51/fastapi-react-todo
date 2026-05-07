from pydantic import BaseModel
from datetime import date


class TaskBase(BaseModel):
    title: str
    description: str
    date: date
    status: str = "todo"


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True



