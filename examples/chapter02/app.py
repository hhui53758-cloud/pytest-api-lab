"""教学被测服务。第二章增加任务创建、查询和删除。"""

from itertools import count
from typing import Literal

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Task API 教学服务", version="0.2.0")

# 第二章先使用内存存储。服务重启后数据清空；后续章节改用 SQLite。
tasks: dict[int, dict] = {}
task_ids = count(1)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    status: Literal["pending", "running", "done"] = "pending"


@app.get("/health")
def health():
    """接口约定：HTTP 200，返回服务状态和名称。"""
    return {"status": "ok", "service": "task-api"}


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    task = {"id": next(task_ids), **payload.model_dump()}
    tasks[task["id"]] = task
    return task


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return Response(status_code=204)


if __name__ == "__main__":
    # 直接运行本文件时启动服务；被其他模块导入时不启动。
    uvicorn.run(app, host="127.0.0.1", port=8000)
