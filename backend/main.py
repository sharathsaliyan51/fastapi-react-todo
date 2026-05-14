from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend import schemas, crud
from backend.database import get_db

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    tasks_db = crud.get_all_tasks(db)
    return templates.TemplateResponse(request, "index.html", {
        "request": request,
        "message": "My Task List",
        "tasks": tasks_db
    })


@app.post("/add-task")
def add_task(title: str = Form(...), description: str = Form(...), date: str = Form(...), db: Session = Depends(get_db)):
    try:
        task_date = datetime.fromisoformat(date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be in YYYY-MM-DD format")
    
    task = schemas.TaskCreate(title=title, description=description, date=task_date)
    crud.create_task(db, task)
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete-task/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/update-task/{task_id}")
def update_task(task_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    crud.update_task_status(db, task_id, status)
    return RedirectResponse(url="/", status_code=303)
