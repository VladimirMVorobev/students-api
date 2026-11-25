from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import engine
from auth_models import User, UserSession
from auth import (
    hash_password,
    verify_password,
    create_token,
    hash_token,
    get_expiration,
)


router = APIRouter(prefix="/auth", tags=["Авторизация"])


class UserData(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


@router.post("/register", status_code=201)
def register(data: UserData):
    with Session(engine) as session:
        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            role="user",
        )

        session.add(user)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Пользователь уже существует",
            )

        return {
            "message": "Пользователь зарегистрирован",
            "username": user.username,
        }


@router.post("/login")
def login(data: UserData):
    with Session(engine) as session:
        user = session.query(User).filter(
            User.username == data.username
        ).first()

        if user is None or not verify_password(
            data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Неверный логин или пароль",
            )

        token = create_token()

        user_session = UserSession(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=get_expiration(),
        )

        session.add(user_session)
        session.commit()

        return {
            "access_token": token,
            "token_type": "bearer",
        }