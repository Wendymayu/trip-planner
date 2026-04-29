"""LLM服务模块"""

import os
from hello_agents import HelloAgentsLLM
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例(单例模式)

    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()

        # 设置超时时间到环境变量(HelloAgentsLLM会读取)
        os.environ.setdefault("LLM_TIMEOUT", str(settings.llm_timeout))

        # HelloAgentsLLM会自动从环境变量读取配置
        _llm_instance = HelloAgentsLLM()

        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型: {_llm_instance.model}")
        print(f"   超时: {settings.llm_timeout}秒")

    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None
