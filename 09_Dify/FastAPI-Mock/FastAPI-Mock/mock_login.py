from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.models import Response
from pydantic import BaseModel
import pymysql
from pymysql import MySQLError
from datetime import datetime

from fastapi.responses import StreamingResponse

app = FastAPI(
    title="Simple Login API",
    description="A basic FastAPI application demonstrating login and register functionality with MySQL database."
)

# Database configuration
DB_CONFIG = {
    'host': '172.17.237.123',
    'port': 3306,
    'db': 'test_db',
    'user': 'student',
    'password': 'Student123ABC!',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


class LoginRequest(BaseModel):
    username: str
    password: str


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

# 函数的传入的参数、返回结果、逻辑
@app.post("/login")
async def login(request: LoginRequest):
    """Authenticate user with username and password"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 传入的用户+密码， 已有是不是一样的
            sql = "SELECT * FROM user WHERE user_name = %s AND user_password = %s"
            cursor.execute(sql, (request.username, request.password))
            user = cursor.fetchone()

        if user:
            return {
                "message": f"Login successful for user: {request.username}",
                "code": 200,
                "user": user
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    except MySQLError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
    finally:
        connection.close()


@app.post("/register")
async def register(request: LoginRequest):
    """Register a new user"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check if username exists
            sql = "SELECT id FROM user WHERE user_name = %s"
            cursor.execute(sql, (request.username,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )

            # Insert new user
            sql = "INSERT INTO user (user_name, user_password) VALUES (%s, %s)"
            cursor.execute(sql, (request.username, request.password))
            connection.commit()

            return {
                "message": f"User {request.username} registered successfully",
                "code": 201
            }
    except MySQLError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        connection.close()


@app.get("/current_year")
async def get_current_year() -> str:
    return str(datetime.now().year)


@app.get("/current_month")
async def get_current_month() -> str:
    return str(datetime.now().month)


from io import BytesIO
import random
from PIL import Image, ImageDraw
import asyncio

async def get_random_image2() -> dict:

    width = random.randint(100, 800)
    height = random.randint(100, 800)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    # Create a simple image with a random solid color
    img = Image.new('RGB', (width, height), color)

    # Add some random shapes for variety
    draw = ImageDraw.Draw(img)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return buffer

@app.get("/random_image")
async def get_random_image() -> dict:
    image_buffer = await get_random_image2()
    return StreamingResponse(image_buffer, media_type="image/jpeg")


# HTTP 对应函数
# fastapi 网络编程框架

# uvicorn main:app --reload --port 8889 --host 0.0.0.0
