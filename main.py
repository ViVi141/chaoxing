# -*- coding: utf-8 -*-
import argparse
import configparser
import random
import time
import sys
import os
import traceback
from urllib3 import disable_warnings, exceptions

from api.logger import logger
from api.base import Chaoxing, Account
from api.exceptions import LoginError, InputFormatError, MaxRollBackExceeded
from api.answer import Tiku
from api.notification import Notification
from api.config_validator import ConfigValidator
from api.secure_config import SecureConfig
from api.course_processor import CourseProcessor, RollBackManager

# 关闭警告
disable_warnings(exceptions.InsecureRequestWarning)


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Samueli924/chaoxing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--use-cookies", action="store_true", help="使用cookies登录")

    parser.add_argument(
        "-c", "--config", type=str, default=None, help="使用配置文件运行程序"
    )
    parser.add_argument("-u", "--username", type=str, default=None, help="手机号账号")
    parser.add_argument("-p", "--password", type=str, default=None, help="登录密码")
    parser.add_argument(
        "-l", "--list", type=str, default=None, help="要学习的课程ID列表, 以 , 分隔"
    )
    parser.add_argument(
        "-s", "--speed", type=float, default=1.0, help="视频播放倍速 (默认1, 最大2)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        "--debug",
        action="store_true",
        help="启用调试模式, 输出DEBUG级别日志",
    )
    parser.add_argument(
        "-a",
        "--notopen-action",
        type=str,
        default="retry",
        choices=["retry", "ask", "continue"],
        help="遇到关闭任务点时的行为: retry-重试, ask-询问, continue-继续",
    )

    # 在解析之前捕获 -h 的行为
    if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"}:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def load_config_from_file(config_path):
    """从配置文件加载设置"""
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf8")

    common_config = {}
    tiku_config = {}
    notification_config = {}

    # 检查并读取common节
    if config.has_section("common"):
        common_config = dict(config.items("common"))
        # 处理course_list，将字符串转换为列表
        if "course_list" in common_config and common_config["course_list"]:
            common_config["course_list"] = [
                item.strip()
                for item in common_config["course_list"].split(",")
                if item.strip()
            ]
        # 处理speed，将字符串转换为浮点数
        if "speed" in common_config:
            try:
                common_config["speed"] = float(common_config["speed"])
            except (ValueError, TypeError):
                logger.warning(f"speed配置无效，使用默认值1.0")
                common_config["speed"] = 1.0
        # 处理notopen_action，设置默认值为retry
        if "notopen_action" not in common_config:
            common_config["notopen_action"] = "retry"
        if "use_cookies" in common_config:
            common_config["use_cookies"] = str_to_bool(common_config["use_cookies"])
        if "username" in common_config and common_config["username"] is not None:
            common_config["username"] = common_config["username"].strip()
        if "password" in common_config and common_config["password"] is not None:
            password = common_config["password"].strip()
            # 检查密码是否加密
            password_encrypted = str_to_bool(
                common_config.get("password_encrypted", "false")
            )
            if password_encrypted:
                logger.debug("检测到加密密码，正在解密...")
                secure_config = SecureConfig()
                decrypted_password = secure_config.decrypt_password(password)
                if decrypted_password:
                    common_config["password"] = decrypted_password
                    logger.debug("密码解密成功")
                else:
                    logger.error("密码解密失败，请检查配置")
                    common_config["password"] = None
            else:
                common_config["password"] = password

    # 检查并读取tiku节
    if config.has_section("tiku"):
        tiku_config = dict(config.items("tiku"))
        # 处理数值类型转换
        for key in ["delay", "cover_rate"]:
            if key in tiku_config:
                try:
                    tiku_config[key] = float(tiku_config[key])
                except (ValueError, TypeError):
                    logger.warning(f"tiku配置{key}无效，使用默认值")
                    if key == "delay":
                        tiku_config[key] = 1.0
                    elif key == "cover_rate":
                        tiku_config[key] = 0.8

    # 检查并读取notification节
    if config.has_section("notification"):
        notification_config = dict(config.items("notification"))

    return common_config, tiku_config, notification_config


def build_config_from_args(args):
    """从命令行参数构建配置"""
    common_config = {
        "use_cookies": args.use_cookies,
        "username": args.username,
        "password": args.password,
        "course_list": (
            [item.strip() for item in args.list.split(",") if item.strip()]
            if args.list
            else None
        ),
        "speed": args.speed if args.speed else 1.0,
        "notopen_action": args.notopen_action if args.notopen_action else "retry",
    }
    return common_config, {}, {}


def init_config():
    """初始化配置"""
    args = parse_args()

    if args.config:
        return load_config_from_file(args.config)
    else:
        return build_config_from_args(args)


def init_chaoxing(common_config, tiku_config):
    """初始化超星实例"""
    username = common_config.get("username", "")
    password = common_config.get("password", "")
    use_cookies = common_config.get("use_cookies", False)

    # 如果没有提供用户名密码，从命令行获取
    if (not username or not password) and not use_cookies:
        username = input("请输入你的手机号, 按回车确认\n手机号:")
        password = input("请输入你的密码, 按回车确认\n密码:")

    account = Account(username, password)

    # 设置题库
    tiku = Tiku()
    tiku.config_set(tiku_config)  # 载入配置
    tiku = tiku.get_tiku_from_config()  # 载入题库
    tiku.init_tiku()  # 初始化题库

    # 获取查询延迟设置
    query_delay = tiku_config.get("delay", 0)

    # 实例化超星API
    chaoxing = Chaoxing(account=account, tiku=tiku, query_delay=query_delay)

    return chaoxing


def filter_courses(all_course, course_list):
    """过滤要学习的课程"""
    if not course_list:
        # 手动输入要学习的课程ID列表
        print("*" * 10 + "课程列表" + "*" * 10)
        for course in all_course:
            print(f"ID: {course['courseId']} 课程名: {course['title']}")
        print("*" * 28)
        try:
            course_list = input(
                "请输入想要学习的课程列表,以逗号分隔,例: 2151141,189191,198198\n"
            ).split(",")
        except Exception as e:
            raise InputFormatError("输入格式错误") from e

    # 筛选需要学习的课程
    course_task = []
    for course in all_course:
        if course["courseId"] in course_list:
            course_task.append(course)

    # 如果没有指定课程，则学习所有课程
    if not course_task:
        course_task = all_course

    return course_task


def main():
    """主程序入口"""
    try:
        # 初始化配置
        common_config, tiku_config, notification_config = init_config()

        # 配置验证
        validator = ConfigValidator()
        is_valid, errors = validator.validate_all_config(
            common_config, tiku_config, notification_config
        )
        if not is_valid:
            logger.error("配置文件验证失败:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("请修正配置文件后重试")
            sys.exit(1)
        logger.info("配置文件验证通过")

        # 强制播放按照配置文件调节
        speed = min(2.0, max(1.0, common_config.get("speed", 1.0)))
        notopen_action = common_config.get("notopen_action", "retry")

        # 初始化超星实例
        chaoxing = init_chaoxing(common_config, tiku_config)

        # 设置外部通知
        notification = Notification()
        notification.config_set(notification_config)
        notification = notification.get_notification_from_config()
        notification.init_notification()

        # 检查当前登录状态
        _login_state = chaoxing.login(
            login_with_cookies=common_config.get("use_cookies", False)
        )
        if not _login_state["status"]:
            raise LoginError(_login_state["msg"])

        # 获取所有的课程列表
        all_course = chaoxing.get_course_list()

        # 过滤要学习的课程
        course_task = filter_courses(all_course, common_config.get("course_list"))

        # 开始学习
        logger.info(f"课程列表过滤完毕, 当前课程任务数量: {len(course_task)}")

        # 使用CourseProcessor进行学习（新方式）
        processor = CourseProcessor(
            chaoxing=chaoxing, speed=speed, notopen_action=notopen_action
        )
        result = processor.process_courses(course_task)

        logger.info("所有课程学习任务已完成")
        notification.send(
            f"chaoxing : 所有课程学习任务已完成 (成功:{result['completed']}/{result['total']})"
        )

    except SystemExit as e:
        if e.code != 0:
            logger.error(f"错误: 程序异常退出, 返回码: {e.code}")
        sys.exit(e.code)
    except KeyboardInterrupt as e:
        logger.error(f"错误: 程序被用户手动中断, {e}")
    except BaseException as e:
        logger.error(f"错误: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        try:
            notification.send(
                f"chaoxing : 出现错误 {type(e).__name__}: {e}\n{traceback.format_exc()}"
            )
        except Exception:
            pass  # 如果通知发送失败，忽略异常
        raise e


if __name__ == "__main__":
    main()
