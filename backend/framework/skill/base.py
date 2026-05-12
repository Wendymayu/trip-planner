"""Skill 基类（极简版）

所有 Skill 来自开源 skill.md 格式，通过 SkillLoader 加载。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SkillResult:
    """Skill 执行结果"""
    success: bool
    output: Any
    error: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


class Skill(ABC):
    """Skill 抽象基类（供 MetadataSkill 继承）"""

    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = None

    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        """执行 Skill"""
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
