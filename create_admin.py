from getpass import getpass
from sqlalchemy.orm import Session
from models import engine
from auth_models import User, UserSession
from auth import hash_password

password = getpass("Введите новый пароль администратора: ")

if len(password) < 12:
    print("Пароль должен содержать минимум 12 символов!")
    raise SystemExit

with Session(engine) as session:
    user = session.query(User).filter_by(
        username="admin"
    ).first()

    if user is None:
        user = User(username="admin")
        session.add(user)

    user.password_hash = hash_password(password)
    user.role = "admin"

    session.flush()
    session.query(UserSession).filter_by(
        user_id=user.id
    ).delete()

    session.commit()
    print("Пароль администратора успешно установлен!")