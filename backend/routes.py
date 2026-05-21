from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from backend import crud, schemas
from backend.database import get_db
from backend.templates import templates

router = APIRouter(prefix="/tasks")
    
@router.get("/", name="home")
def home(request: Request, db:  Session = Depends(get_db)):
    tasks_db = crud.get_all_tasks(db)
    return templates.TemplateResponse(request, "index2.html", {
        "request": request,
        "message": "My Task List",
        "tasks": tasks_db,
        "current_filter": "all",
    })

@router.post("/add-task", name="add_task")
def add_task(request: Request, title: str = Form(...), description: str = Form(...), date: str = Form(...), db: Session = Depends(get_db)):
    try:
        task_date = datetime.fromisoformat(date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format")
    
    task = schemas.TaskCreate(title=title, description=description, date=task_date)
    crud.create_task(db, task)
    return RedirectResponse(url=request.url_for("home"), status_code=303)

@router.post("/delete-task/{task_id}", name="delete_task")
def delete_task(request: Request, task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)
    return RedirectResponse(url=request.url_for("home"), status_code=303)

@router.post("/update-task/{task_id}", name="update_task")
def update_task(request: Request, task_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    crud.update_task_status(db, task_id, status)
    return RedirectResponse(url=request.url_for("home"), status_code=303)

@router.get("/task_filter", name="task_filter")
def task_filter(request: Request, search_dropdown: str = Query("all"), search_string: str = Form(""), db: Session = Depends(get_db)):
    tasks_db = crud.get_all_tasks(db, search_string, search_dropdown)
    return templates.TemplateResponse(request, "index2.html", {
        "request": request,
        "message": "My Task List",
        "tasks": tasks_db,
        "current_filter": search_dropdown,
        "search_string": search_string,
    })
