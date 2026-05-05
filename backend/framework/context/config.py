"""上下文配置"""

from dataclasses import dataclass


@dataclass
class ContextConfig:
    """上下文预算配置

    Args:
        max_tokens: 总 token 预算（包含输入和输出）
        reserve_for_response: 为模型响应预留的 token 数
    """

    max_tokens: int = 8000
    reserve_for_response: int = 1000

    @property
    def budget(self) -> int:
        """可用输入 token 预算"""
        return self.max_tokens - self.reserve_for_response
