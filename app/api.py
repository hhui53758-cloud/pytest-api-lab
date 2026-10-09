"""登录、任务 CRUD 与所有权检查；供本地学习使用。"""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from app.database import Database

ROOT = Path(__file__).resolve().parents[1]


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=50)
    status: Literal["pending", "running", "done"] = "pending"


def create_app(db_path=None):
    database = Database(db_path or os.getenv("TASK_API_DB", ROOT / "data" / "demo.sqlite3"))

    @asynccontextmanager
    async def lifespan(application):
        database.initialize()
        application.state.database = database
        yield

    application = FastAPI(title="Task API Lab", version="1.0.0", lifespan=lifespan)
    bearer = HTTPBearer(auto_error=False)

    def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
        user_id = database.user_for_token(credentials.credentials) if credentials else None
        if user_id is None:
            raise HTTPException(status_code=401, detail="Authentication required",
                                headers={"WWW-Authenticate": "Bearer"})
        return user_id

    def owned_task(task_id, user_id):
        task = database.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return task

    @application.get("/health")
    def health():
        return {"status": "ok", "service": "task-api"}

    @application.post("/auth/login")
    def login(payload: LoginInput):
        token = database.authenticate(payload.username, payload.password)
        if token is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"access_token": token, "token_type": "bearer"}

    @application.post("/tasks", status_code=201)
    def create_task(payload: TaskInput, user_id: Annotated[int, Depends(current_user)]):
        return database.create_task(user_id, payload.title, payload.status)

    @application.get("/tasks/{task_id}")
    def get_task(task_id: int, user_id: Annotated[int, Depends(current_user)]):
        return owned_task(task_id, user_id)

    @application.put("/tasks/{task_id}")
    def update_task(task_id: int, payload: TaskInput, user_id: Annotated[int, Depends(current_user)]):
        owned_task(task_id, user_id)
        return database.update_task(task_id, payload.title, payload.status)

    @application.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int, user_id: Annotated[int, Depends(current_user)]):
        owned_task(task_id, user_id)
        database.delete_task(task_id)
        return Response(status_code=204)

    return application
