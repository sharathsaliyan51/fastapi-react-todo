from sqlalchemy import Column, Integer, String, Date, ForeignKey

from backend.database import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="todo", nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"),  nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="")
    status = Column(String, default="active", nullable=False)
