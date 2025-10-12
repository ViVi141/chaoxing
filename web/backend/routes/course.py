"""
课程相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from loguru import logger

from auth import get_current_active_user
from database import get_db
from models import User
from api.base import Chaoxing, Account
from api.secure_config import SecureConfig

router = APIRouter()


@router.get("/list", response_model=List[Dict[str, Any]])
async def get_course_list(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户的超星课程列表
    
    需要用户已配置超星账号
    """
    try:
        # 预加载配置关系
        await db.refresh(current_user, ['config'])
        
        if not current_user.config:
            raise HTTPException(
                status_code=400,
                detail="请先配置超星账号"
            )
        
        config = current_user.config
        
        # 检查是否配置了账号
        if not config.cx_username or not config.cx_password_encrypted:
            raise HTTPException(
                status_code=400,
                detail="请先在配置管理中填写超星账号和密码"
            )
        
        # 解密密码
        secure_config = SecureConfig()
        cx_password = secure_config.decrypt_password(config.cx_password_encrypted)
        
        if not cx_password:
            raise HTTPException(
                status_code=400,
                detail="密码解密失败，请重新配置密码"
            )
        
        # 创建Account对象
        account = Account(
            _username=config.cx_username,
            _password=cx_password
        )
        
        # 创建Chaoxing实例
        chaoxing = Chaoxing(account=account, tiku=None, query_delay=0)
        
        # 登录
        logger.info(f"用户 {current_user.username} 正在获取课程列表...")
        login_result = chaoxing.login(login_with_cookies=config.use_cookies)
        
        if not login_result["status"]:
            raise HTTPException(
                status_code=400,
                detail=f"登录超星失败: {login_result['msg']}"
            )
        
        # 获取课程列表
        course_list = chaoxing.get_course_list()
        
        logger.info(f"成功获取 {len(course_list)} 门课程")
        
        # 格式化课程信息
        formatted_courses = []
        for course in course_list:
            formatted_courses.append({
                "courseId": course.get("courseId"),
                "courseName": course.get("title", "未命名课程"),
                "teacherName": course.get("teacherfactor", ""),
                "clazzId": course.get("clazzId"),
                "cpi": course.get("cpi"),
                "progress": course.get("progress", 0),
                "state": course.get("state", 0),  # 0: 进行中, 1: 已结束
            })
        
        return formatted_courses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取课程列表失败: {str(e)}"
        )

