from sqlalchemy import literal, func, or_, and_
from sqlalchemy.orm import Session, load_only
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from backend import models, schemas


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(
        title=task.title,
        description=task.description,
        date=task.date
    )
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_task


def get_all_tasks(db: Session, search_string: str = "", search_dropdown: str = "all") -> list[models.Task]:

    s_lit = literal(search_string)
    search_dropdown_pattern = literal(search_dropdown)

    pattern = func.concat('%', func.coalesce(s_lit, ''), '%')


    print(f"search_string: {search_string}")
    print(f"literal: {s_lit}, pattern: {pattern}")

    query = (
        db.query(models.Task)
        .options(load_only(models.Task.id, models.Task.title, models.Task.description, models.Task.date, models.Task.status))
        .filter(
            and_(
                or_(
                    func.coalesce(s_lit, '') == '',              # search empty/null -> match all
                    models.Task.title.ilike(pattern),             # otherwise match title
                    models.Task.description.ilike(pattern),       # or description
                ),
                or_(
                    func.coalesce(search_dropdown_pattern, 'all') == 'all',        # filter "all" -> match all
                    models.Task.status == search_dropdown_pattern,          # otherwise match status
                ),
            )
        )
    )
    
    results = query.all()
    return results

def delete_task(db: Session, task_id: int) -> None:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
def update_task_status(db: Session, task_id: int, status: str) -> models.Task:
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if status not in {"todo", "in_progress", "done"}:
        raise HTTPException(status_code=400, detail="Invalid task status")
    try:
        task.status = status
        db.commit()
        db.refresh(task)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    return task


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password_hash
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_user