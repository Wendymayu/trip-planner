"""会话记忆实现"""
from collections import deque
from typing import List, Optional

from .base import Memory
from .message import Message


class ConversationMemory(Memory):
    """
    会话记忆，在内存中存储对话历史

    支持滑动窗口限制消息数量，防止上下文过长。
    """

    def __init__(self, max_messages: Optional[int] = None):
        """
        初始化会话记忆

        Args:
            max_messages: 最大消息数量，None 表示不限制
        """
        self.max_messages = max_messages
        # 使用 deque 实现滑动窗口
        self._messages: deque = deque(maxlen=max_messages) if max_messages else []

    def add(self, message: Message) -> None:
        """添加消息"""
        self._messages.append(message)

    def get_all(self) -> List[Message]:
        """获取所有消息"""
        return list(self._messages)

    def get_recent(self, n: int = 10) -> List[Message]:
        """获取最近 n 条消息"""
        messages = list(self._messages)
        return messages[-n:] if n < len(messages) else messages

    def clear(self) -> None:
        """清空记忆"""
        self._messages.clear()

    def __len__(self) -> int:
        """返回消息数量"""
        return len(self._messages)

    def __repr__(self) -> str:
        return f"ConversationMemory(messages={len(self._messages)}, max={self.max_messages})"


if __name__ == "__main__":
    # 测试
    memory = ConversationMemory(max_messages=5)

    # 添加消息
    memory.add(Message.user("你好"))
    memory.add(Message.assistant("你好！有什么可以帮你的？"))
    memory.add(Message.user("我叫张三"))
    memory.add(Message.assistant("你好张三！"))

    print(f"消息数量: {len(memory)}")
    print(f"所有消息: {memory.get_all()}")
    print(f"最近 2 条: {memory.get_recent(2)}")

    # 测试滑动窗口
    for i in range(5):
        memory.add(Message.user(f"消息 {i}"))

    print(f"\n添加 5 条后，消息数量: {len(memory)}")  # 应该还是 5
    print(f"消息内容: {[m.content for m in memory.get_all()]}")

    # 测试 build_messages
    memory2 = ConversationMemory()
    memory2.add(Message.user("你好"))
    memory2.add(Message.assistant("你好！"))

    messages = memory2.build_messages(
        system_prompt="你是一个助手",
        user_input="今天天气怎么样？"
    )
    print(f"\n构建的消息列表:")
    for m in messages:
        print(f"  {m}")
