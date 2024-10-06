from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session
from app.schemas.schemas import TokenResponse, UserCreate, LoginFrom
from app.database.database import get_db
from app.controllers.auth_controller import (
    login_user,
    logout_user,
    refresh_access_token,
    register_new_user,
)


router = APIRouter(prefix="/")


@router.get("/")
async def login(
    form_data: LoginFrom,
    db: Session = Depends(get_db),
    response: Response = Response(),
):
    return login_user(form_data, db, response)
