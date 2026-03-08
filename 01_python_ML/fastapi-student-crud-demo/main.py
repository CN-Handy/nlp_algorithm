from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

# FastAPI Python后端开发的框架： 用来部署模型、部署项目的代码
# 创建 FastAPI 应用实例
app = FastAPI(
    title="学生管理API",
    description="一个简单的 FastAPI 应用，用于管理学生信息。",
    version="1.0.0"
)


# 使用 Pydantic 定义学生数据模型，用于请求体和响应体
class Student(BaseModel):
    """
    学生数据模型
    """
    name: str
    age: int
    major: str


# 模拟一个数据库，使用字典存储学生信息
# 键为学生ID (整数)，值为 Student 对象
db_students: Dict[int, Student] = {}
next_student_id = 1


@app.get("/")
def hello_world():
    return "你好，我爱机器学习"

# 增删改查 crud

@app.post("/students/", status_code=201, summary="创建新学生")
def create_student(student: Student):
    """
    创建一个新学生。

    - **name**: 学生姓名
    - **age**: 学生年龄
    - **major**: 学生专业
    """
    global next_student_id
    db_students[next_student_id] = student
    student_id = next_student_id
    next_student_id += 1
    return {"id": student_id, **student.dict()}


@app.get("/students/", summary="列出所有学生")
def list_students():
    """
    返回数据库中所有学生的列表。
    """
    # 将字典转换为包含 ID 和学生信息的列表
    students_with_id = [{"id": student_id, **student.dict()} for student_id, student in db_students.items()]
    return students_with_id


@app.get("/students/{student_id}", summary="获取单个学生信息")
def get_student(student_id: int):
    """
    根据学生ID返回单个学生信息。
    """
    student = db_students.get(student_id)
    if not student:
        # 如果找不到学生，返回 404 Not Found 错误
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student_id, **student.dict()}


@app.delete("/students/{student_id}", summary="删除一个学生")
def delete_student(student_id: int):
    """
    根据学生ID删除一个学生。
    """
    if student_id not in db_students:
        # 如果要删除的学生不存在，返回 404 Not Found 错误
        raise HTTPException(status_code=404, detail="Student not found")

    del db_students[student_id]
    return {"message": f"Student with ID {student_id} deleted successfully"}

