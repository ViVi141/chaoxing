# -*- coding: utf-8 -*-
"""
测试题库功能
"""
import pytest
from unittest.mock import Mock, patch
from api.answer import Tiku


@pytest.mark.unit
class TestTiku:
    """测试题库基类"""
    
    def test_tiku_initialization(self):
        """测试题库初始化"""
        tiku = Tiku()
        # Tiku基类默认是禁用的
        assert hasattr(tiku, 'DISABLE')
        assert hasattr(tiku, 'SUBMIT')
    
    def test_config_set(self):
        """测试配置设置"""
        tiku = Tiku()
        config = {
            "provider": "AI",
            "ai_key": "test_key"
        }
        tiku.config_set(config)
        assert tiku._conf == config
    
    def test_get_tiku_from_config_default(self):
        """测试默认题库（无配置）"""
        tiku = Tiku()
        result = tiku.get_tiku_from_config()
        # 无配置时返回自身（DISABLE=True）
        assert isinstance(result, Tiku)
    
    def test_init_tiku(self):
        """测试题库初始化"""
        tiku = Tiku()
        # 调用init_tiku不应该出错
        tiku.init_tiku()
        assert True  # 如果没有异常就通过
    
    def test_query_method_exists(self):
        """测试query方法存在"""
        tiku = Tiku()
        assert hasattr(tiku, 'query')

