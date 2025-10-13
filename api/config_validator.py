# -*- coding: utf-8 -*-
"""
配置验证模块
提供配置文件参数校验功能
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from api.logger import logger


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        验证手机号格式

        Args:
            phone: 手机号

        Returns:
            (是否有效, 错误信息)
        """
        if not phone or phone.strip() == "" or phone == "xxx":
            return False, "手机号不能为空或使用模板值"

        # 中国手机号正则：1开头，第二位3-9，共11位
        pattern = r"^1[3-9]\d{9}$"
        if not re.match(pattern, phone.strip()):
            return False, f"手机号格式不正确: {phone}"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        验证密码

        Args:
            password: 密码

        Returns:
            (是否有效, 错误信息)
        """
        if not password or password.strip() == "" or password == "xxx":
            return False, "密码不能为空或使用模板值"

        if len(password) < 6:
            return False, "密码长度不能少于6位"

        return True, ""

    @staticmethod
    def validate_speed(speed: float) -> Tuple[bool, str]:
        """
        验证播放倍速

        Args:
            speed: 播放倍速

        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(speed, (int, float)):
            return False, f"播放倍速必须是数字: {speed}"

        if speed < 1.0 or speed > 2.0:
            return False, f"播放倍速必须在1.0到2.0之间: {speed}"

        return True, ""

    @staticmethod
    def validate_notopen_action(action: str) -> Tuple[bool, str]:
        """
        验证未开放任务点处理方式

        Args:
            action: 处理方式

        Returns:
            (是否有效, 错误信息)
        """
        valid_actions = ["retry", "ask", "continue"]
        if action not in valid_actions:
            return (
                False,
                f"无效的notopen_action: {action}，有效值: {', '.join(valid_actions)}",
            )

        return True, ""

    @staticmethod
    def validate_course_list(course_list: Optional[List[str]]) -> Tuple[bool, str]:
        """
        验证课程列表

        Args:
            course_list: 课程ID列表

        Returns:
            (是否有效, 错误信息)
        """
        if course_list is None or len(course_list) == 0:
            return True, ""  # 空列表表示学习所有课程

        for course_id in course_list:
            if not course_id.strip():
                return False, "课程ID不能为空"
            # 课程ID应该是数字
            if not course_id.strip().isdigit():
                return False, f"课程ID必须是数字: {course_id}"

        return True, ""

    @staticmethod
    def validate_tiku_config(tiku_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证题库配置

        Args:
            tiku_config: 题库配置字典

        Returns:
            (是否有效, 错误信息)
        """
        if not tiku_config or not tiku_config.get("provider"):
            return True, ""  # 未配置题库，跳过验证

        provider = tiku_config.get("provider", "")
        valid_providers = ["TikuYanxi", "TikuLike", "TikuAdapter", "AI", "SiliconFlow"]

        if provider not in valid_providers:
            return (
                False,
                f"无效的题库provider: {provider}，有效值: {', '.join(valid_providers)}",
            )

        # 验证submit参数
        submit = str(tiku_config.get("submit", "false")).lower()
        if submit not in ["true", "false"]:
            logger.warning(f"submit参数值异常: {submit}，将视为false")

        # 验证cover_rate
        try:
            cover_rate = float(tiku_config.get("cover_rate", 0.8))
            if cover_rate < 0 or cover_rate > 1:
                return False, f"cover_rate必须在0到1之间: {cover_rate}"
        except (ValueError, TypeError):
            return False, f"cover_rate必须是数字: {tiku_config.get('cover_rate')}"

        # 验证delay
        try:
            delay = float(tiku_config.get("delay", 0))
            if delay < 0:
                return False, f"delay不能为负数: {delay}"
        except (ValueError, TypeError):
            return False, f"delay必须是数字: {tiku_config.get('delay')}"

        # 根据不同题库验证特定配置
        if provider == "TikuYanxi":
            tokens = tiku_config.get("tokens", "")
            if not tokens or tokens.strip() == "":
                return False, "言溪题库需要配置tokens参数"

        elif provider == "TikuLike":
            tokens = tiku_config.get("tokens", "")
            if not tokens or tokens.strip() == "":
                return False, "LIKE知识库需要配置tokens参数"

        elif provider == "TikuAdapter":
            url = tiku_config.get("url", "")
            if not url or url.strip() == "":
                return False, "TikuAdapter需要配置url参数"
            # 简单URL格式验证
            if not url.startswith("http://") and not url.startswith("https://"):
                return False, f"TikuAdapter的url格式不正确: {url}"

        elif provider == "AI":
            endpoint = tiku_config.get("endpoint", "")
            key = tiku_config.get("key", "")
            model = tiku_config.get("model", "")
            if not endpoint or not key or not model:
                return False, "AI题库需要配置endpoint、key和model参数"

        elif provider == "SiliconFlow":
            key = tiku_config.get("siliconflow_key", "")
            if not key or key.strip() == "":
                return False, "硅基流动需要配置siliconflow_key参数"

        return True, ""

    @staticmethod
    def validate_notification_config(
        notification_config: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        验证通知配置

        Args:
            notification_config: 通知配置字典

        Returns:
            (是否有效, 错误信息)
        """
        if not notification_config or not notification_config.get("provider"):
            return True, ""  # 未配置通知，跳过验证

        provider = notification_config.get("provider", "")
        valid_providers = ["ServerChan", "Qmsg", "Bark"]

        if provider not in valid_providers:
            return (
                False,
                f"无效的通知provider: {provider}，有效值: {', '.join(valid_providers)}",
            )

        url = notification_config.get("url", "")
        if not url or url.strip() == "":
            return False, f"{provider}通知需要配置url参数"

        if not url.startswith("http://") and not url.startswith("https://"):
            return False, f"通知url格式不正确: {url}"

        return True, ""

    @classmethod
    def validate_common_config(cls, common_config: Dict[str, Any]) -> List[str]:
        """
        验证通用配置

        Args:
            common_config: 通用配置字典

        Returns:
            错误信息列表
        """
        errors = []

        # 如果不使用cookies登录，则需要验证账号密码
        use_cookies = common_config.get("use_cookies", False)
        if not use_cookies:
            username = common_config.get("username", "")
            password = common_config.get("password", "")

            valid, msg = cls.validate_phone_number(username)
            if not valid:
                errors.append(msg)

            valid, msg = cls.validate_password(password)
            if not valid:
                errors.append(msg)

        # 验证播放倍速
        speed = common_config.get("speed", 1.0)
        valid, msg = cls.validate_speed(speed)
        if not valid:
            errors.append(msg)

        # 验证notopen_action
        notopen_action = common_config.get("notopen_action", "retry")
        valid, msg = cls.validate_notopen_action(notopen_action)
        if not valid:
            errors.append(msg)

        # 验证课程列表
        course_list = common_config.get("course_list")
        valid, msg = cls.validate_course_list(course_list)
        if not valid:
            errors.append(msg)

        return errors

    @classmethod
    def validate_all_config(
        cls,
        common_config: Dict[str, Any],
        tiku_config: Dict[str, Any],
        notification_config: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        验证所有配置

        Args:
            common_config: 通用配置
            tiku_config: 题库配置
            notification_config: 通知配置

        Returns:
            (是否全部有效, 错误信息列表)
        """
        all_errors = []

        # 验证通用配置
        errors = cls.validate_common_config(common_config)
        all_errors.extend(errors)

        # 验证题库配置
        valid, msg = cls.validate_tiku_config(tiku_config)
        if not valid:
            all_errors.append(msg)

        # 验证通知配置
        valid, msg = cls.validate_notification_config(notification_config)
        if not valid:
            all_errors.append(msg)

        return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    # 测试验证器
    validator = ConfigValidator()

    # 测试手机号验证
    print("测试手机号验证:")
    print(validator.validate_phone_number("13800138000"))
    print(validator.validate_phone_number("12345678901"))
    print(validator.validate_phone_number("xxx"))

    # 测试密码验证
    print("\n测试密码验证:")
    print(validator.validate_password("123456"))
    print(validator.validate_password("12345"))
    print(validator.validate_password("xxx"))

    # 测试倍速验证
    print("\n测试倍速验证:")
    print(validator.validate_speed(1.5))
    print(validator.validate_speed(3.0))
    print(validator.validate_speed(0.5))
