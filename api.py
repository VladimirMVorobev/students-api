from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Student, engine
from database_manager import DatabaseManager


app = FastAPI(title="Students API")
db = DatabaseManager(engine)


class StudentData(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    grade: int = Field(ge=0, le=100)


@app.get("/")
def home():
    return {"message": "Students API работает!"}


@app.get("/students")
def get_students():
    return db.select_students()


@app.get("/students/{student_id}")
def get_student(student_id: int):
    with Session(engine) as session:
        student = session.get(Student, student_id)

        if student is None:
            raise HTTPException(status_code=404, detail="Студент не найден")

        return {
            "id": student.id,
            "last_name": student.last_name,
            "first_name": student.first_name,
            "faculty": student.faculty,
            "course": student.course,
            "grade": student.grade,
        }


@app.post("/students", status_code=201)
def create_student(data: StudentData):
    student_id = db.insert_student(
        data.last_name,
        data.first_name,
        data.faculty,
        data.course,
        data.grade,
    )
    return {"message": "Студент добавлен", "id": student_id}


@app.put("/students/{student_id}")
def update_student(student_id: int, data: StudentData):
    updated = db.update_student(
        student_id,
        data.last_name,
        data.first_name,
        data.faculty,
        data.course,
        data.grade,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")

    return {"message": "Данные студента обновлены"}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    deleted = db.delete_student(student_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Студент не найден")

    return {"message": "Студент удалён"}
