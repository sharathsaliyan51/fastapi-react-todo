
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend import crud
from backend.database import get_db
from backend.schemas import UserCreate
from backend.templates import templates


router = APIRouter(prefix="/users")

@router.get("/me")
def read_users():
    return {"message": "List of users"}

@router.get("/register", name="register_form")
def register_form(request: Request):
    return templates.TemplateResponse(request, "user_register.html", {
        "request": request,
        "message": "Create Account",
    })

@router.post("/register", name="register_user")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):

    user_response = crud.create_user(db, user)
    return {
        "id": user_response.id,
        "username": user_response.username,
        "email": user_response.email,
    }

@router.post("/login")
async def user_login(request: Request, db: Session = Depends(get_db)):
    body = await request.json()  # Ensure the body is read before accessing it
    print("Logging in user...")
    print(f"Request data: {body}")
    return {"message": "User login endpoint"} 
