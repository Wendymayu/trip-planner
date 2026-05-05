"""记忆工厂类"""
from typing import Dict, Any

from .base import Memory
from .conversation import ConversationMemory


class MemoryFactory:
    """
    记忆工厂，用于创建不同类型的记忆实例

    支持注册新的记忆类型，便于扩展。
    """

    _registry: Dict[str, type] = {
        "conversation": ConversationMemory,
    }

    @classmethod
    def register(cls, name: str, memory_class: type) -> None:
        """
        注册新的记忆类型

        Args:
            name: 记忆类型名称
            memory_class: 记忆类（必须继承 Memory）
        """
        if not isinstance(memory_class, type) or not issubclass(memory_class, Memory):
            raise ValueError(f"{memory_class} 必须是 Memory 的子类")
        cls._registry[name] = memory_class

    @classmethod
    def create(cls, memory_type: str = "conversation", **kwargs) -> Memory:
        """
        创建记忆实例

        Args:
            memory_type: 记忆类型
            **kwargs: 传递给记忆类的参数

        Returns:
            记忆实例

        Raises:
            ValueError: 记忆类型未注册
        """
        if memory_type not in cls._registry:
            raise ValueError(
                f"未知的记忆类型: {memory_type}。可用类型: {list(cls._registry.keys())}"
            )
        return cls._registry[memory_type](**kwargs)

    @classmethod
    def list_available(cls) -> list:
        """列出所有可用的记忆类型"""
        return list(cls._registry.keys())


if __name__ == "__main__":
    # 测试工厂
    print("可用记忆类型:", MemoryFactory.list_available())

    # 创建会话记忆
    memory = MemoryFactory.create("conversation", max_messages=10)
    print(f"创建的记忆: {memory}")

    # 注册自定义记忆类型（示例）
    class CustomMemory(Memory):
        def __init__(self, prefix: str = ""):
            self.prefix = prefix
            self._messages = []

        def add(self, message):
            self._messages.append(message)

        def get_all(self):
            return self._messages

        def get_recent(self, n=10):
            return self._messages[-n:]

        def clear(self):
            self._messages.clear()

    MemoryFactory.register("custom", CustomMemory)
    print("注册后可用类型:", MemoryFactory.list_available())

    custom = MemoryFactory.create("custom", prefix="[TEST]")
    print(f"自定义记忆: {custom}")