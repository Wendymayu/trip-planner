"""上下文工程模块

提供 Token 计数和预算控制功能。

使用示例:
    from framework.context import ContextManager, ContextConfig

    manager = ContextManager(ContextConfig(max_tokens=4000))
    messages = manager.build(system_prompt="你是助手", history=[], user_input="你好")
"""

from .config import ContextConfig
from .tokenizer import TokenCounter
from .manager import ContextManager

__all__ = ["ContextConfig", "TokenCounter", "ContextManager"]
