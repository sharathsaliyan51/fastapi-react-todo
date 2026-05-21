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

class Test(BaseModel):
    id: int
    name: str
    status: str

    class Config:
        from_attributes = True


#  user model
class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str


class UserLogin(BaseModel):
    username: str
    password_hash: str


class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True