# -*- coding: utf-8 -*-
"""
API限流中间件
使用slowapi实现请求频率限制，防止API滥用和暴力攻击
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from starlette.responses import JSONResponse


def get_real_ip(request: Request) -> str:
    """
    获取真实IP地址
    
    考虑代理和负载均衡的情况：
    1. X-Forwarded-For (标准代理头)
    2. X-Real-IP (Nginx常用)
    3. 直接连接IP
    """
    # 如果通过代理，获取真实IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For可能包含多个IP，取第一个
        return forwarded.split(",")[0].strip()
    
    # Nginx的Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接连接的IP
    return get_remote_address(request)


# 创建限流器实例
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["200/minute", "2000/hour"],  # 默认限制
    storage_uri="memory://",  # 使用内存存储（生产环境建议用Redis）
    strategy="fixed-window",  # 固定窗口策略
    headers_enabled=True,  # 启用响应头
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    自定义限流超出处理
    返回友好的JSON错误信息
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "请求过于频繁",
            "detail": f"已超过请求限制：{exc.detail}",
            "retry_after": exc.headers.get("Retry-After", "60")
        },
        headers=exc.headers
    )


# 限流规则配置
RATE_LIMITS = {
    # 认证相关 - 严格限制
    "auth_login": "5/minute",           # 登录：每分钟5次
    "auth_register": "3/hour",          # 注册：每小时3次
    "auth_password_reset": "3/hour",    # 密码重置：每小时3次
    "auth_verify_email": "10/hour",     # 邮箱验证：每小时10次
    
    # 任务相关 - 中等限制
    "task_create": "20/minute",         # 创建任务：每分钟20次
    "task_list": "100/minute",          # 查询任务：每分钟100次
    "task_action": "30/minute",         # 任务操作：每分钟30次
    
    # 配置相关 - 中等限制
    "config_update": "30/minute",       # 更新配置：每分钟30次
    "config_test": "10/minute",         # 配置测试：每分钟10次
    
    # 管理员相关 - 较宽松
    "admin_query": "200/minute",        # 管理查询：每分钟200次
    "admin_action": "50/minute",        # 管理操作：每分钟50次
    
    # 通用API - 默认限制
    "general": "100/minute",            # 通用接口：每分钟100次
}


def get_rate_limit(endpoint_type: str) -> str:
    """
    根据端点类型获取限流规则
    
    Args:
        endpoint_type: 端点类型（如 'auth_login', 'task_create'）
    
    Returns:
        限流规则字符串（如 '5/minute'）
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["general"])


# IP白名单（可选）
# 生产环境中，可以将可信IP加入白名单
WHITELIST_IPS = [
    "127.0.0.1",
    "::1",
]


def is_whitelisted(request: Request) -> bool:
    """
    检查IP是否在白名单中
    
    Args:
        request: FastAPI请求对象
    
    Returns:
        是否在白名单中
    """
    client_ip = get_real_ip(request)
    return client_ip in WHITELIST_IPS


# 使用示例（在app.py中）:
#
# from middleware.rate_limit import limiter, rate_limit_exceeded_handler, get_rate_limit
#
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
#
# # 在路由中使用：
# @app.post("/api/auth/login")
# @limiter.limit(get_rate_limit("auth_login"))
# async def login(request: Request, ...):
#     ...

