# -*- coding: utf-8 -*-
"""
HTTP客户端优化模块
提供改进的请求重试和超时机制
"""
import time
from typing import Any, Callable, Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.logger import logger


class ImprovedHTTPAdapter(HTTPAdapter):
    """改进的HTTP适配器，增强重试和超时控制"""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Tuple[int, ...] = (500, 502, 503, 504, 408, 429),
        **kwargs,
    ):
        """
        初始化适配器

        Args:
            max_retries: 最大重试次数
            backoff_factor: 退避因子，重试间隔 = backoff_factor * (2 ^ (重试次数-1))
            status_forcelist: 需要重试的HTTP状态码
            **kwargs: 传递给父类的其他参数
        """
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
            raise_on_status=False,
        )
        super().__init__(max_retries=retry_strategy, **kwargs)


class RequestWithRetry:
    """带重试机制的请求封装"""

    DEFAULT_TIMEOUT = (10, 30)  # (连接超时, 读取超时)

    @staticmethod
    def create_session(
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        pool_connections: int = 10,
        pool_maxsize: int = 20,
    ) -> requests.Session:
        """
        创建一个配置好的Session对象

        Args:
            max_retries: 最大重试次数
            backoff_factor: 退避因子
            pool_connections: 连接池数量
            pool_maxsize: 连接池最大大小

        Returns:
            配置好的Session对象
        """
        session = requests.Session()

        adapter = ImprovedHTTPAdapter(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @classmethod
    def get_with_retry(
        cls,
        url: str,
        max_attempts: int = 3,
        timeout: Optional[Tuple[int, int]] = None,
        **kwargs,
    ) -> Optional[requests.Response]:
        """
        带重试的GET请求

        Args:
            url: 请求URL
            max_attempts: 最大尝试次数
            timeout: 超时设置 (连接超时, 读取超时)
            **kwargs: 其他requests参数

        Returns:
            Response对象，失败返回None
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT

        session = kwargs.pop("session", None)
        if session is None:
            session = cls.create_session()

        for attempt in range(1, max_attempts + 1):
            try:
                response = session.get(url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"GET请求超时 (尝试 {attempt}/{max_attempts}): {url}")
                if attempt < max_attempts:
                    time.sleep(1 * attempt)  # 递增等待
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts:
                    time.sleep(2 * attempt)
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP错误 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts and response.status_code in (
                    500,
                    502,
                    503,
                    504,
                ):
                    time.sleep(2 * attempt)
                else:
                    return response  # 对于其他HTTP错误，直接返回
            except Exception as e:
                logger.error(f"请求异常 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts:
                    time.sleep(1 * attempt)

        logger.error(f"GET请求失败，已达最大尝试次数: {url}")
        return None

    @classmethod
    def post_with_retry(
        cls,
        url: str,
        max_attempts: int = 3,
        timeout: Optional[Tuple[int, int]] = None,
        **kwargs,
    ) -> Optional[requests.Response]:
        """
        带重试的POST请求

        Args:
            url: 请求URL
            max_attempts: 最大尝试次数
            timeout: 超时设置 (连接超时, 读取超时)
            **kwargs: 其他requests参数

        Returns:
            Response对象，失败返回None
        """
        if timeout is None:
            timeout = cls.DEFAULT_TIMEOUT

        session = kwargs.pop("session", None)
        if session is None:
            session = cls.create_session()

        for attempt in range(1, max_attempts + 1):
            try:
                response = session.post(url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"POST请求超时 (尝试 {attempt}/{max_attempts}): {url}")
                if attempt < max_attempts:
                    time.sleep(1 * attempt)
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts:
                    time.sleep(2 * attempt)
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP错误 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts and response.status_code in (
                    500,
                    502,
                    503,
                    504,
                ):
                    time.sleep(2 * attempt)
                else:
                    return response
            except Exception as e:
                logger.error(f"请求异常 (尝试 {attempt}/{max_attempts}): {url} - {e}")
                if attempt < max_attempts:
                    time.sleep(1 * attempt)

        logger.error(f"POST请求失败，已达最大尝试次数: {url}")
        return None


def with_timeout_and_retry(
    max_retries: int = 3,
    timeout: Tuple[int, int] = (10, 30),
    backoff_factor: float = 1.0,
):
    """
    装饰器：为函数添加超时和重试机制

    Args:
        max_retries: 最大重试次数
        timeout: 超时设置
        backoff_factor: 退避因子

    Returns:
        装饰后的函数
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    # 如果函数参数中有timeout，设置它
                    if "timeout" in kwargs:
                        kwargs["timeout"] = timeout

                    result = func(*args, **kwargs)
                    return result

                except (
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                ) as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} 调用失败 (尝试 {attempt}/{max_retries}): {e}"
                    )

                    if attempt < max_retries:
                        sleep_time = backoff_factor * (2 ** (attempt - 1))
                        logger.debug(f"等待 {sleep_time} 秒后重试...")
                        time.sleep(sleep_time)

                except Exception as e:
                    logger.error(f"{func.__name__} 发生未预期的异常: {e}")
                    raise

            logger.error(f"{func.__name__} 失败，已达最大重试次数")
            raise last_exception

        return wrapper

    return decorator


if __name__ == "__main__":
    # 测试请求重试
    print("测试GET请求重试:")
    response = RequestWithRetry.get_with_retry("https://www.baidu.com", max_attempts=3)
    if response:
        print(f"请求成功，状态码: {response.status_code}")
    else:
        print("请求失败")

    print("\n测试装饰器:")

    @with_timeout_and_retry(max_retries=3, timeout=(5, 10))
    def test_request():
        response = requests.get("https://www.baidu.com", timeout=(5, 10))
        return response.status_code

    try:
        status = test_request()
        print(f"装饰器测试成功，状态码: {status}")
    except Exception as e:
        print(f"装饰器测试失败: {e}")
