# -*- coding: utf-8 -*-
"""
安全配置管理模块
提供配置文件密码加密/解密功能
"""
import base64
import hashlib
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from api.logger import logger


class SecureConfig:
    """安全配置管理器，用于加密存储敏感信息"""

    def __init__(self, key_file: str = ".config_key"):
        """
        初始化安全配置管理器

        Args:
            key_file: 密钥文件路径
        """
        self.key_file = Path(key_file)
        self.cipher = None
        self._initialize_cipher()

    def _generate_key_from_password(self, password: str) -> bytes:
        """
        从密码生成加密密钥

        Args:
            password: 用户密码

        Returns:
            加密密钥
        """
        # 使用PBKDF2从密码派生密钥
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            b"chaoxing_salt_2024",  # 固定盐值
            100000,  # 迭代次数
        )
        return base64.urlsafe_b64encode(key)

    def _initialize_cipher(self) -> None:
        """初始化加密器"""
        if self.key_file.exists():
            # 读取现有密钥
            try:
                with open(self.key_file, "rb") as f:
                    key = f.read()
                self.cipher = Fernet(key)
                logger.debug("已加载现有加密密钥")
            except Exception as e:
                logger.error(f"加载加密密钥失败: {e}")
                self.cipher = None
        else:
            # 首次使用，生成新密钥
            self._create_new_key()

    def _create_new_key(self) -> None:
        """创建新的加密密钥"""
        key = Fernet.generate_key()
        try:
            with open(self.key_file, "wb") as f:
                f.write(key)
            # 设置文件权限（仅所有者可读写）
            if os.name != "nt":  # Unix系统
                os.chmod(self.key_file, 0o600)
            self.cipher = Fernet(key)
            logger.info("已生成新的加密密钥")
        except Exception as e:
            logger.error(f"创建加密密钥失败: {e}")
            self.cipher = None

    def encrypt_password(self, password: str) -> Optional[str]:
        """
        加密密码

        Args:
            password: 明文密码

        Returns:
            加密后的密码（Base64编码），失败返回None
        """
        if not self.cipher:
            logger.warning("加密器未初始化，无法加密密码")
            return None

        try:
            encrypted = self.cipher.encrypt(password.encode("utf-8"))
            return base64.urlsafe_b64encode(encrypted).decode("utf-8")
        except Exception as e:
            logger.error(f"密码加密失败: {e}")
            return None

    def decrypt_password(self, encrypted_password: str) -> Optional[str]:
        """
        解密密码

        Args:
            encrypted_password: 加密的密码（Base64编码）

        Returns:
            明文密码，失败返回None
        """
        if not self.cipher:
            logger.warning("加密器未初始化，无法解密密码")
            return None

        try:
            encrypted_bytes = base64.urlsafe_b64decode(
                encrypted_password.encode("utf-8")
            )
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except InvalidToken:
            logger.error("密码解密失败: 密钥不匹配或数据损坏")
            return None
        except Exception as e:
            logger.error(f"密码解密失败: {e}")
            return None

    def is_encrypted(self, value: str) -> bool:
        """
        判断字符串是否为加密格式

        Args:
            value: 待判断的字符串

        Returns:
            是否为加密格式
        """
        # 简单判断：加密后的字符串通常很长且包含特定字符
        if not value or len(value) < 40:
            return False

        try:
            # 尝试Base64解码
            base64.urlsafe_b64decode(value.encode("utf-8"))
            return True
        except Exception:
            return False


def migrate_config_to_encrypted(config_path: str) -> bool:
    """
    将配置文件中的明文密码迁移为加密密码

    Args:
        config_path: 配置文件路径

    Returns:
        是否成功迁移
    """
    import configparser

    config = configparser.ConfigParser()
    try:
        config.read(config_path, encoding="utf8")
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return False

    if not config.has_section("common"):
        logger.warning("配置文件中没有[common]节")
        return False

    password = config.get("common", "password", fallback=None)
    if not password or password == "xxx":
        logger.info("未配置密码或密码为模板值，跳过加密")
        return True

    secure_config = SecureConfig()

    # 检查密码是否已加密
    if secure_config.is_encrypted(password):
        logger.info("密码已加密，无需重复处理")
        return True

    # 加密密码
    encrypted_password = secure_config.encrypt_password(password)
    if not encrypted_password:
        logger.error("密码加密失败")
        return False

    # 更新配置文件
    config.set("common", "password", encrypted_password)
    config.set("common", "password_encrypted", "true")

    try:
        with open(config_path, "w", encoding="utf8") as f:
            config.write(f)
        logger.info(f"配置文件密码已加密: {config_path}")
        return True
    except Exception as e:
        logger.error(f"写入配置文件失败: {e}")
        return False


if __name__ == "__main__":
    # 测试加密功能
    sc = SecureConfig()

    test_password = "test123456"
    print(f"原始密码: {test_password}")

    encrypted = sc.encrypt_password(test_password)
    print(f"加密后: {encrypted}")

    decrypted = sc.decrypt_password(encrypted)
    print(f"解密后: {decrypted}")

    print(f"加密解密是否一致: {test_password == decrypted}")
