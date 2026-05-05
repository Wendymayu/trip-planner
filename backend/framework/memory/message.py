"""消息数据结构"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class Message:
    """对话消息，存储 user 或 assistant 的内容"""
    role: str  # "user" 或 "assistant"
    content: str
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于 LLM 调用"""
        return {"role": self.role, "content": self.content}

    @classmethod
    def user(cls, content: str) -> "Message":
        """创建用户消息"""
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        """创建助手消息"""
        return cls(role="assistant", content=content)
