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


def get_all_tasks(db: Session) -> list[models.Task]:
    return db.query(models.Task).options(
        load_only(
            models.Task.id,
            models.Task.title,
            models.Task.description,
            models.Task.date,
            models.Task.status,
        )
    ).all()

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
