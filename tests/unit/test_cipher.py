# -*- coding: utf-8 -*-
"""
测试加密解密功能
"""
import pytest
from api.cipher import AESCipher
from api.secure_config import SecureConfig


@pytest.mark.unit
class TestAESCipher:
    """测试AES加密类（仅加密功能）"""
    
    def test_cipher_initialization(self):
        """测试密码器初始化"""
        cipher = AESCipher()
        assert cipher is not None
        assert cipher.key is not None
        assert cipher.iv is not None
    
    def test_encrypt_basic(self):
        """测试基本加密功能"""
        cipher = AESCipher()
        original_text = "测试数据123"
        
        # 加密
        encrypted = cipher.encrypt(original_text)
        assert encrypted != original_text
        assert len(encrypted) > 0
        assert isinstance(encrypted, str)
    
    def test_encrypt_empty_string(self):
        """测试加密空字符串"""
        cipher = AESCipher()
        encrypted = cipher.encrypt("")
        assert len(encrypted) > 0  # 即使空字符串也会产生密文
    
    def test_encrypt_special_characters(self):
        """测试加密特殊字符"""
        cipher = AESCipher()
        special_text = "!@#$%^&*()_+-=[]{}|;':\"<>,.?/~`"
        
        encrypted = cipher.encrypt(special_text)
        assert len(encrypted) > 0
    
    def test_encrypt_unicode(self):
        """测试加密Unicode字符"""
        cipher = AESCipher()
        unicode_text = "你好世界测试"
        
        encrypted = cipher.encrypt(unicode_text)
        assert len(encrypted) > 0
    
    def test_encrypt_consistency(self):
        """测试加密一致性（相同输入产生相同密文）"""
        cipher = AESCipher()
        text = "一致性测试"
        
        encrypted1 = cipher.encrypt(text)
        encrypted2 = cipher.encrypt(text)
        
        # AESCipher使用固定IV，相同明文会产生相同密文
        assert encrypted1 == encrypted2


@pytest.mark.unit
class TestSecureConfig:
    """测试SecureConfig加密类（完整加密解密）"""
    
    def test_secure_config_initialization(self):
        """测试SecureConfig初始化"""
        import tempfile
        import os
        from cryptography.fernet import Fernet
        
        # 创建临时密钥文件
        key_file = tempfile.mktemp()
        try:
            # 生成并保存密钥
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            config = SecureConfig(key_file=key_file)
            assert config is not None
            assert config.cipher is not None
        finally:
            if os.path.exists(key_file):
                os.remove(key_file)
    
    def test_encrypt_decrypt_password(self):
        """测试密码加密和解密"""
        import tempfile
        import os
        from cryptography.fernet import Fernet
        
        # 创建临时密钥文件
        key_file = tempfile.mktemp()
        try:
            # 生成并保存密钥
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            config = SecureConfig(key_file=key_file)
            original_password = "Test123456!"
            
            # 加密
            encrypted = config.encrypt_password(original_password)
            assert encrypted is not None
            assert encrypted != original_password
            assert len(encrypted) > 0
            
            # 解密
            decrypted = config.decrypt_password(encrypted)
            assert decrypted == original_password
        finally:
            if os.path.exists(key_file):
                os.remove(key_file)
    
    def test_encrypt_decrypt_unicode_password(self):
        """测试Unicode密码加密解密"""
        import tempfile
        import os
        from cryptography.fernet import Fernet
        
        # 创建临时密钥文件
        key_file = tempfile.mktemp()
        try:
            # 生成并保存密钥
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            config = SecureConfig(key_file=key_file)
            password = "密码测试123!@#"
            
            encrypted = config.encrypt_password(password)
            decrypted = config.decrypt_password(encrypted)
            
            assert decrypted == password
        finally:
            if os.path.exists(key_file):
                os.remove(key_file)

