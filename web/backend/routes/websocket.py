# -*- coding: utf-8 -*-
"""
WebSocket路由
"""
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, AsyncSessionLocal
from models import User, Task
from routes.auth import AuthService
import json
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from api.logger import logger

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储用户ID到WebSocket连接的映射
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储任务ID到订阅用户列表的映射
        self.task_subscribers: Dict[int, set] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"用户{user_id}建立WebSocket连接")

    def disconnect(self, user_id: int):
        """断开连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # 清理任务订阅
        for task_id in list(self.task_subscribers.keys()):
            if user_id in self.task_subscribers[task_id]:
                self.task_subscribers[task_id].remove(user_id)
                if not self.task_subscribers[task_id]:
                    del self.task_subscribers[task_id]
        logger.info(f"用户{user_id}断开WebSocket连接")

    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(user_id)

    async def send_task_update(self, task_id: int, data: dict):
        """发送任务更新"""
        if task_id in self.task_subscribers:
            for user_id in self.task_subscribers[task_id]:
                await self.send_personal_message(
                    {"type": "task_update", "task_id": task_id, "data": data}, user_id
                )

    async def subscribe_task(self, task_id: int, user_id: int):
        """订阅任务更新"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(user_id)
        logger.debug(f"用户{user_id}订阅任务{task_id}")

    async def unsubscribe_task(self, task_id: int, user_id: int):
        """取消订阅任务"""
        if (
            task_id in self.task_subscribers
            and user_id in self.task_subscribers[task_id]
        ):
            self.task_subscribers[task_id].remove(user_id)
            if not self.task_subscribers[task_id]:
                del self.task_subscribers[task_id]
            logger.debug(f"用户{user_id}取消订阅任务{task_id}")


# 全局连接管理器
manager = ConnectionManager()


async def get_current_user_ws(token: str) -> User:
    """
    从WebSocket令牌获取当前用户
    """
    payload = AuthService.verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # 创建新的数据库会话
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket, token: str = Query(..., description="JWT令牌")
):
    """
    WebSocket连接端点

    客户端需要在URL参数中提供JWT令牌：
    ws://localhost:8000/ws/connect?token=your_jwt_token
    """
    # 验证令牌
    user = await get_current_user_ws(token)
    if not user or not user.is_active:
        await websocket.close(code=1008, reason="认证失败或账号被禁用")
        return

    # 建立连接
    await manager.connect(user.id, websocket)

    try:
        # 发送欢迎消息
        await websocket.send_json(
            {
                "type": "connected",
                "message": "WebSocket连接成功",
                "user_id": user.id,
                "username": user.username,
            }
        )

        # 保持连接并处理消息
        while True:
            try:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理不同类型的消息
                if message.get("type") == "subscribe_task":
                    task_id = message.get("task_id")
                    if task_id:
                        # 验证任务所有权
                        async with AsyncSessionLocal() as db:
                            result = await db.execute(
                                select(Task).where(
                                    Task.id == task_id, Task.user_id == user.id
                                )
                            )
                            task = result.scalar_one_or_none()
                            if task:
                                await manager.subscribe_task(task_id, user.id)
                                await websocket.send_json(
                                    {
                                        "type": "subscribed",
                                        "task_id": task_id,
                                        "message": f"已订阅任务{task_id}的更新",
                                    }
                                )
                            else:
                                await websocket.send_json(
                                    {"type": "error", "message": "任务不存在或无权访问"}
                                )

                elif message.get("type") == "unsubscribe_task":
                    task_id = message.get("task_id")
                    if task_id:
                        await manager.unsubscribe_task(task_id, user.id)
                        await websocket.send_json(
                            {
                                "type": "unsubscribed",
                                "task_id": task_id,
                                "message": f"已取消订阅任务{task_id}",
                            }
                        )

                elif message.get("type") == "ping":
                    # 心跳响应
                    await websocket.send_json({"type": "pong"})

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"未知的消息类型: {message.get('type')}",
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "无效的JSON格式"}
                )

    except WebSocketDisconnect:
        manager.disconnect(user.id)
        logger.info(f"用户{user.id}主动断开WebSocket连接")

    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(user.id)


# 辅助函数：从Celery任务中调用，推送任务进度
async def push_task_progress(
    task_id: int, progress: int, status: str, message: str = None
):
    """
    推送任务进度更新

    从Celery任务中调用此函数来实时推送进度
    """
    await manager.send_task_update(
        task_id, {"progress": progress, "status": status, "message": message}
    )


# 辅助函数：推送系统通知
async def push_notification(user_id: int, message: str, level: str = "info"):
    """
    推送系统通知

    Args:
        user_id: 用户ID
        message: 通知消息
        level: 级别（info/warning/error）
    """
    await manager.send_personal_message(
        {"type": "notification", "level": level, "message": message}, user_id
    )
