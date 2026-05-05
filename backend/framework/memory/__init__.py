"""
记忆系统模块

提供可扩展的记忆实现，支持会话记忆及后续扩展。

使用示例:
    from framework.memory import ConversationMemory, Message

    # 创建会话记忆
    memory = ConversationMemory(max_messages=20)

    # 添加消息
    memory.add(Message.user("你好"))
    memory.add(Message.assistant("你好！"))

    # 获取历史
    messages = memory.get_all()
"""

from .message import Message
from .base import Memory
from .conversation import ConversationMemory
from .factory import MemoryFactory

__all__ = [
    "Message",
    "Memory",
    "ConversationMemory",
    "MemoryFactory",
]
