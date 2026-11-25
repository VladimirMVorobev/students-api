from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models import engine
from auth_models import User, UserSession
from auth import hash_token


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется авторизация"
        )

    token_hash = hash_token(credentials.credentials)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    with Session(engine) as session:
        user_session = session.query(UserSession).filter(
            UserSession.token_hash == token_hash,
            UserSession.expires_at > now
        ).first()

        if user_session is None:
            raise HTTPException(
                status_code=401,
                detail="Недействительный или просроченный токен"
            )

        user = session.get(User, user_session.user_id)

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Пользователь не найден"
            )

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }


def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав"
        )

    return user