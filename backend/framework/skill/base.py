"""Skill 基类（极简版）

所有 Skill 来自开源 skill.md 格式，通过 SkillLoader 加载。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Skill(ABC):
    """Skill 抽象基类"""

    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = None

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行 Skill，返回 dict 或 str"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """生成 LLM 可理解的 schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {"type": "object", "properties": {}},
            }
        }
