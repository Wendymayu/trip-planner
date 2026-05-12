import sys
import json
from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class ToolSchema:
    """工具定义，包含函数和参数schema"""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema 格式
    func: Callable

    def to_openai_format(self) -> Dict[str, Any]:
        """转换为 OpenAI function calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """工具注册表，支持OpenAI function calling"""

    def __init__(self):
        self.tools: Dict[str, ToolSchema] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        注册工具

        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            parameters: 参数定义 (JSON Schema 格式)
        """
        if parameters is None:
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }

        self.tools[name] = ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
            func=func
        )

    def get_tool(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        tool_schema = self.tools.get(name)
        return tool_schema.func if tool_schema else None

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """生成 OpenAI function calling 格式的工具列表"""
        return [tool.to_openai_format() for tool in self.tools.values()]

    def register_skill(self, skill) -> None:
        """将 Skill 注册为 Tool（早绑定）

        Args:
            skill: Skill 对象
        """
        self.tools[skill.name] = ToolSchema(
            name=skill.name,
            description=skill.description,
            parameters=skill.parameters,
            func=skill.execute
        )

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        执行工具并返回结果

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果的字符串表示
        """
        tool_schema = self.tools.get(name)
        if not tool_schema:
            return f"错误：未找到工具 '{name}'"

        try:
            result = tool_schema.func(**arguments)
            if isinstance(result, str):
                return result
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return f"工具执行错误: {str(e)}"


# ============ 示例工具 ============

def query_location() -> Dict[str, Any]:
    """查询当前地理位置"""
    return {"city": "北京", "latitude": 39.9042, "longitude": 116.4074}


def query_weather(city: str, date: str = None) -> str:
    """查询天气"""
    return f"{city}的天气是晴朗，温度25度。"


if __name__ == "__main__":
    # 示例：创建工具注册表并注册工具
    registry = ToolRegistry()

    # 注册位置查询工具
    registry.register(
        name="query_location",
        func=query_location,
        description="查询当前用户的地理位置，返回城市名称和经纬度坐标",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )

    # 注册天气查询工具
    registry.register(
        name="query_weather",
        func=query_weather,
        description="根据城市名称查询天气信息",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如：北京、上海"
                },
                "date": {
                    "type": "string",
                    "description": "查询日期，格式：YYYY-MM-DD，可选"
                }
            },
            "required": ["city"]
        }
    )

    # 测试：生成 OpenAI 格式的工具列表
    print("=== OpenAI Tools Schema ===")
    tools_schema = registry.get_openai_tools()
    for tool in tools_schema:
        print(json.dumps(tool, ensure_ascii=False, indent=2))

    # 测试：执行工具
    print("\n=== 执行工具 ===")
    result = registry.execute("query_location", {})
    print(f"位置查询结果: {result}")

    result = registry.execute("query_weather", {"city": "北京"})
    print(f"天气查询结果: {result}")
