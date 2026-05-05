"""上下文管理器

整合 token 计数、预算控制和上下文缩减。
"""

import sys
import os
from typing import List, Dict, Any
sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

from framework.context.config import ContextConfig
from framework.context.tokenizer import TokenCounter


class ContextManager:
    """上下文管理器

    使用示例:
        manager = ContextManager(config)
        messages = manager.build(
            system_prompt="你是助手",
            history=memory.get_all(),
            user_input="你好"
        )
    """

    def __init__(self, config: ContextConfig = None):
        self.config = config or ContextConfig()
        self.counter = TokenCounter()

    def build(
        self,
        system_prompt: str,
        history: List[Any] = None,
        user_input: str = "",
        additional: List[Dict[str, Any]] = None,
        keep_last_n: int = 2,
    ) -> List[Dict[str, Any]]:
        """构建符合 token 预算的消息列表

        Args:
            system_prompt: 系统提示词
            history: 历史消息（Message 对象或字典）
            user_input: 当前用户输入
            additional: 额外消息（如工具调用）
            keep_last_n: 保留最近 N 轮对话

        Returns:
            消息列表（OpenAI 格式）
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            for msg in history:
                messages.append(msg.to_dict() if hasattr(msg, "to_dict") else msg)

        if additional:
            messages.extend(additional)

        if user_input:
            messages.append({"role": "user", "content": user_input})

        # 检查并缩减
        current = self.counter.count_messages(messages)
        if current > self.config.budget:
            messages = self._reduce(messages, self.config.budget, keep_last_n)

        return messages

    def _reduce(
        self,
        messages: List[Dict[str, Any]],
        target: int,
        keep_last_n: int,
    ) -> List[Dict[str, Any]]:
        """缩减上下文：保留系统消息 + 最近 N 轮 + 从新到旧填充

        Args:
            messages: 消息列表
            target: 目标 token 数
            keep_last_n: 保留最近 N 轮

        Returns:
            缩减后的消息列表
        """
        # 分离系统消息
        system_msgs = [m for m in messages if m.get("role") == "system"]
        other_msgs = [m for m in messages if m.get("role") != "system"]

        # 系统消息 token 数
        system_tokens = sum(self.counter.count_message(m) for m in system_msgs)
        available = target - system_tokens

        # 保护最近 N 轮（N 条 user + N 条 assistant）
        protected = []
        if keep_last_n > 0 and len(other_msgs) >= keep_last_n * 2:
            protected = other_msgs[-(keep_last_n * 2):]
            other_msgs = other_msgs[:-(keep_last_n * 2)]

        protected_tokens = sum(self.counter.count_message(m) for m in protected)
        available -= protected_tokens

        # 从新到旧选择（保留新消息）
        selected = []
        total = 0
        for msg in reversed(other_msgs):
            tokens = self.counter.count_message(msg)
            if total + tokens > available:
                break
            selected.insert(0, msg)
            total += tokens

        return system_msgs + selected + protected

    def statistics(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取 token 统计"""
        total = self.counter.count_messages(messages)
        return {
            "total": total,
            "budget": self.config.budget,
            "remaining": self.config.budget - total,
        }


if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class MockMessage:
        role: str
        content: str
        def to_dict(self):
            return {"role": self.role, "content": self.content}

    history = [
        MockMessage("user", "你好"),
        MockMessage("assistant", "你好！有什么可以帮助你的？"),
        MockMessage("user", "我想去北京旅游"),
        MockMessage("assistant", "北京是个很好的选择！你计划什么时候去？"),
        MockMessage("user", "下个月十五号左右"),
        MockMessage("assistant", "好的，下个月十五号正值秋季，天气很舒适。你想去哪些景点？"),
    ]

    print("=== 测试 ContextManager ===\n")

    # 正常情况
    manager = ContextManager()
    messages = manager.build(
        system_prompt="你是一个旅行规划助手",
        history=history,
        user_input="我想去故宫和长城"
    )
    print(f"正常: {len(messages)} 条, {manager.statistics(messages)}")

    # 超预算
    small_config = ContextConfig(max_tokens=200, reserve_for_response=50)
    manager_small = ContextManager(config=small_config)
    messages_small = manager_small.build(
        system_prompt="你是一个旅行规划助手",
        history=history,
        user_input="我想去故宫和长城"
    )
    print(f"缩减: {len(messages_small)} 条, {manager_small.statistics(messages_small)}")
    for msg in messages_small:
        print(f"  [{msg['role']}]: {msg['content'][:30]}...")
