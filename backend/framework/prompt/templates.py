"""提示词模板

提供可参数化的提示词模板，支持变量占位符和默认值。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import re


@dataclass
class PromptTemplate:
    """提示词模板，支持变量占位符 {{variable}}

    使用示例:
        template = PromptTemplate(
            name="weather",
            template="你是{{city}}的天气助手，任务：{{task}}",
            defaults={"task": "查询天气"}
        )
        prompt = template.render(city="北京")
    """

    name: str
    template: str
    description: str = ""
    defaults: Dict[str, Any] = field(default_factory=dict)

    _variables: List[str] = field(default_factory=list)

    def __post_init__(self):
        """自动提取模板变量"""
        pattern = r'\{\{(\w+)\}\}'
        self._variables = re.findall(pattern, self.template)

    @property
    def variables(self) -> List[str]:
        """返回模板中的变量列表"""
        return self._variables

    def render(self, **kwargs) -> str:
        """渲染模板，替换变量

        Args:
            **kwargs: 变量值

        Returns:
            渲染后的提示词

        Raises:
            ValueError: 缺少必需变量
        """
        # 合并默认值和传入值
        values = {**self.defaults, **kwargs}

        # 验证必需变量
        missing = [v for v in self._variables if v not in values]
        if missing:
            raise ValueError(f"缺少必需变量: {missing}")

        # 替换变量
        result = self.template
        for key, value in values.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))

        return result

    def __repr__(self) -> str:
        return f"PromptTemplate(name='{self.name}', variables={self._variables})"


if __name__ == "__main__":
    # 测试模板
    print("=== 测试 PromptTemplate ===\n")

    template = PromptTemplate(
        name="weather",
        template="你是{{city}}的天气助手，任务：{{task}}。",
        defaults={"task": "查询天气"}
    )

    print(f"模板: {template.template}")
    print(f"变量: {template.variables}")
    print(f"渲染: {template.render(city='北京')}")

