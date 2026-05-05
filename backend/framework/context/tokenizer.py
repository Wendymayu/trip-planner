"""Token 计数器"""

import tiktoken
from typing import List, Dict, Union


class TokenCounter:
    """Token 计数器，基于 tiktoken

    使用示例:
        counter = TokenCounter()
        tokens = counter.count_text("你好世界")
        tokens = counter.count_message({"role": "user", "content": "你好"})
    """

    def __init__(self, encoding_name: str = "cl100k_base"):
        """初始化计数器

        Args:
            encoding_name: 编码名称，cl100k_base 适用于 GPT-4/GPT-3.5
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_text(self, text: str) -> int:
        """计算文本 token 数

        Args:
            text: 文本内容

        Returns:
            token 数量
        """
        return len(self.encoding.encode(text))

    def count_message(self, message: Dict) -> int:
        """计算单条消息 token 数（含格式开销）

        每条消息有固定的格式开销：
        - role: ~4 tokens
        - 结构: ~4 tokens
        - 总计约 4 + 4 = 8 tokens 开销

        Args:
            message: 消息字典，包含 role 和 content

        Returns:
            token 数量
        """
        content = message.get("content", "")
        if content is None:
            content = ""

        # 内容 token 数
        tokens = self.count_text(str(content))

        # 消息格式开销（约 8 tokens）
        tokens += 8

        # 如果有工具调用，额外计算
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                tokens += self.count_text(tc.get("function", {}).get("name", ""))
                tokens += self.count_text(tc.get("function", {}).get("arguments", ""))

        return tokens

    def count_messages(self, messages: List[Dict]) -> int:
        """计算消息列表总 token 数

        Args:
            messages: 消息列表

        Returns:
            token 总数
        """
        total = 0
        for msg in messages:
            total += self.count_message(msg)

        # 回复初始化开销（约 3 tokens）
        total += 3

        return total


if __name__ == "__main__":
    from .config import ContextConfig

    # 测试
    print("=== 测试 TokenCounter ===\n")

    counter = TokenCounter()

    # 测试文本计数
    text = "你好，世界！"
    print(f"'{text}' → {counter.count_text(text)} tokens")

    # 测试消息计数
    messages = [
        {"role": "system", "content": "你是天气助手"},
        {"role": "user", "content": "北京天气怎么样？"},
        {"role": "assistant", "content": "北京今天晴，气温 25 度。"}
    ]

    for msg in messages:
        print(f"[{msg['role']}]: {counter.count_message(msg)} tokens")

    print(f"\n总计: {counter.count_messages(messages)} tokens")

    # 测试预算
    config = ContextConfig()
    print(f"\n预算: {config.budget} tokens (总 {config.max_tokens}，预留 {config.reserve_for_response})")
