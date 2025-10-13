# -*- coding: utf-8 -*-
"""
日志模块
提供日志记录和敏感信息脱敏功能
"""
import re
import sys
from typing import Any, Dict

from loguru import logger


class SensitiveFilter:
    """敏感信息过滤器"""

    @staticmethod
    def mask_phone(text: str) -> str:
        """
        手机号脱敏：保留前3位和后4位

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        pattern = r"1[3-9]\d{9}"

        def replacer(match):
            phone = match.group()
            return f"{phone[:3]}****{phone[-4:]}"

        return re.sub(pattern, replacer, text)

    @staticmethod
    def mask_password(text: str) -> str:
        """
        密码脱敏：替换为****

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        # 匹配常见的密码字段
        patterns = [
            r'(["\']?password["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)(["\']?)',
            r'(["\']?pwd["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)(["\']?)',
            r'(["\']?passwd["\']?\s*[=:]\s*["\']?)([^"\'&\s]+)(["\']?)',
        ]

        result = text
        for pattern in patterns:
            result = re.sub(
                pattern,
                lambda m: f"{m.group(1)}****{m.group(3)}",
                result,
                flags=re.IGNORECASE,
            )

        return result

    @staticmethod
    def mask_token(text: str) -> str:
        """
        Token脱敏：保留前6位和后4位

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        # 匹配常见的token字段（至少20个字符）
        patterns = [
            r'(["\']?token["\']?\s*[=:]\s*["\']?)([a-zA-Z0-9_-]{20,})(["\']?)',
            r'(["\']?key["\']?\s*[=:]\s*["\']?)([a-zA-Z0-9_-]{20,})(["\']?)',
            r'(["\']?apikey["\']?\s*[=:]\s*["\']?)([a-zA-Z0-9_-]{20,})(["\']?)',
        ]

        result = text
        for pattern in patterns:

            def replacer(match):
                token = match.group(2)
                if len(token) >= 10:
                    masked = f"{token[:6]}****{token[-4:]}"
                else:
                    masked = "****"
                return f"{match.group(1)}{masked}{match.group(3)}"

            result = re.sub(pattern, replacer, result, flags=re.IGNORECASE)

        return result

    @staticmethod
    def mask_cookie(text: str) -> str:
        """
        Cookie脱敏

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        # 匹配Cookie值
        pattern = r'(Cookie["\']?\s*[=:]\s*["\']?)([^"\']+)(["\']?)'

        def replacer(match):
            return f"{match.group(1)}****{match.group(3)}"

        return re.sub(pattern, replacer, text, flags=re.IGNORECASE)

    @classmethod
    def mask_all(cls, text: str) -> str:
        """
        对文本进行全面脱敏

        Args:
            text: 原始文本

        Returns:
            脱敏后的文本
        """
        if not isinstance(text, str):
            text = str(text)

        text = cls.mask_phone(text)
        text = cls.mask_password(text)
        text = cls.mask_token(text)
        text = cls.mask_cookie(text)

        return text


def sensitive_filter(record: Dict[str, Any]) -> bool:
    """
    Loguru过滤器，用于脱敏日志消息

    Args:
        record: 日志记录

    Returns:
        是否保留该日志
    """
    if "message" in record:
        record["message"] = SensitiveFilter.mask_all(record["message"])

    return True


# 移除默认的处理器
logger.remove()

# 添加控制台输出（带颜色）
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    filter=sensitive_filter,
)

# 添加文件输出（带日志轮转）
logger.add(
    "logs/chaoxing_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天0点轮转
    retention="30 days",  # 保留30天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
    level="TRACE",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    filter=sensitive_filter,
)

# 添加错误日志文件
logger.add(
    "logs/chaoxing_error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    filter=sensitive_filter,
)


__all__ = ["logger", "SensitiveFilter"]
