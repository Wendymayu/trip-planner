"""记忆抽象基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from .message import Message


class Memory(ABC):
    """
    记忆抽象基类

    定义所有记忆实现必须支持的接口，便于扩展不同记忆策略。
    """

    @abstractmethod
    def add(self, message: Message) -> None:
        """
        添加消息到记忆

        Args:
            message: 要存储的消息
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Message]:
        """
        获取所有消息

        Returns:
            消息列表
        """
        pass

    @abstractmethod
    def get_recent(self, n: int = 10) -> List[Message]:
        """
        获取最近 n 条消息

        Args:
            n: 消息数量

        Returns:
            最近的消息列表
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空记忆"""
        pass

    def build_messages(self, system_prompt: str, user_input: str) -> List[Dict[str, Any]]:
        """
        构建 LLM 调用所需的消息列表

        Args:
            system_prompt: 系统提示词
            user_input: 当前用户输入

        Returns:
            完整的消息列表（OpenAI 格式）
        """
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        for msg in self.get_all():
            messages.append(msg.to_dict())

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})

        return messages
