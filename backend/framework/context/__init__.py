"""上下文工程模块

提供 Token 计数和预算控制功能。

使用示例:
    from framework.context import TokenCounter, ContextConfig

    # 计算 token 数
    counter = TokenCounter()
    tokens = counter.count_text("你好世界")

    # 检查预算
    config = ContextConfig(max_tokens=4000)
    if counter.count_messages(messages) > config.budget:
        # 处理超预算
        pass
"""

from .config import ContextConfig
from .tokenizer import TokenCounter

__all__ = ["ContextConfig", "TokenCounter"]
