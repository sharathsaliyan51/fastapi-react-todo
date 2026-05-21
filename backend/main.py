
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from backend.routes import router as task_router
from backend.user_routes import router as user_router
from backend.templates import templates

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

router = APIRouter(prefix="/api/v1")

# add task routes
router.include_router(task_router)
router.include_router(user_router)

app.include_router(router)

# @app.get("/test_html")
# def home_test(request: Request, db: Session = Depends(get_db)):
#     tasks_db = crud.get_all_tasks(db)
#     return templates.TemplateResponse(request, "index2.html", {
#         "request": request,
#         "message": "My Task List",
#         "tasks": tasks_db
#     })

# @app.get("/test")
# def test():
#     return {"message": "Test successful"}

# @app.post("/create-test")
# def create_test(data: dict=Body(...), db: Session = Depends(get_db)):
#     test = models.Test(
#         name = data.get("name"),
#         status = data.get("status")
#     )
#     db.add(test)
#     db.commit()
#     db.refresh(test)
#     return data 
