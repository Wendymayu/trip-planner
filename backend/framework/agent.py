import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import LLMClient
from tools import ToolRegistry
from memory import Memory, ConversationMemory, Message
from prompt import PromptTemplate


class Agent:
    """支持工具调用、记忆和提示词模板的Agent"""

    def __init__(
        self,
        name: str,
        llm: LLMClient,
        prompt_template: PromptTemplate = None,
        tool_registry: ToolRegistry = None,
        memory: Memory = None
    ):
        self.name = name
        self.llm = llm
        self.tool_registry = tool_registry
        # 默认使用会话记忆
        self.memory = memory if memory is not None else ConversationMemory()

        # 提示词模板
        self.prompt_template = prompt_template

        # 模板变量存储
        self._template_vars = {}

    def act(self, input: str, max_iterations: int = 5) -> str:
        """
        执行任务，支持工具调用循环和记忆

        Args:
            input: 用户输入
            max_iterations: 最大迭代次数，防止无限循环

        Returns:
            Agent的最终响应
        """
        # 使用记忆构建消息列表（包含历史对话）
        system_prompt = self._build_system_prompt()
        messages = self.memory.build_messages(system_prompt, input)

        # 获取工具schema
        tools = None
        if self.tool_registry and len(self.tool_registry.tools) > 0:
            tools = self.tool_registry.get_openai_tools()

        final_response = ""

        # 工具调用循环
        for iteration in range(max_iterations):
            print(f"\n[迭代 {iteration + 1}] 调用LLM...")

            response = self.llm.chat(messages, tools=tools, tool_choice="auto")
            message = response.choices[0].message

            # 检查是否有工具调用
            if not message.tool_calls:
                # 无工具调用，获得最终响应
                print(f"[迭代 {iteration + 1}] 无工具调用，返回结果")
                final_response = message.content or ""
                break

            # 有工具调用，执行工具并继续循环
            print(f"[迭代 {iteration + 1}] 模型请求调用 {len(message.tool_calls)} 个工具")

            # 将assistant消息添加到历史
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # 执行每个工具
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"  - 执行工具: {tool_name}, 参数: {tool_args}")

                # 执行工具
                result = self.tool_registry.execute(tool_name, tool_args)
                print(f"  - 工具结果: {result}")

                # 将工具结果添加到消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result
                })

        # 存储到记忆（只存用户输入和最终响应）
        self.memory.add(Message.user(input))
        self.memory.add(Message.assistant(final_response))

        return final_response

    def clear_memory(self) -> None:
        """清空记忆"""
        self.memory.clear()

    def set_template_vars(self, **kwargs) -> None:
        """设置模板变量

        Args:
            **kwargs: 模板变量键值对
        """
        self._template_vars.update(kwargs)

    def _build_system_prompt(self) -> str:
        """构建系统提示词

        Returns:
            完整的系统提示词
        """
        if self.prompt_template:
            return self.prompt_template.render(**self._template_vars)
        return "你是一个专业的助手"


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # 创建LLM客户端
    llm = LLMClient()

    # 创建工具注册表
    registry = ToolRegistry()
    registry.register(
        name="query_location",
        func=lambda: {"city": "北京", "latitude": 39.9042, "longitude": 116.4074},
        description="查询当前用户的地理位置",
        parameters={"type": "object", "properties": {}, "required": []}
    )
    registry.register(
        name="query_weather",
        func=lambda city, date=None: f"{city}的天气是晴朗，温度25度。",
        description="根据城市名称查询天气信息",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"},
                "date": {"type": "string", "description": "查询日期，可选"}
            },
            "required": ["city"]
        }
    )

    print("=== 测试 Agent 提示词工程 ===\n")

    # 使用提示词模板
    print("--- 测试: 使用提示词模板 ---")
    weather_template = PromptTemplate(
        name="weather",
        template="你是{{city}}的天气助手，任务：{{task}}。当前季节：{{season}}。",
        defaults={"task": "查询和分析天气", "season": "夏季"}
    )

    agent = Agent(
        name="天气助手",
        llm=llm,
        prompt_template=weather_template,
        tool_registry=registry
    )
    agent.set_template_vars(city="北京")
    print(f"系统提示词:\n{agent._build_system_prompt()}\n")

    print("=== 测试 Agent 工具调用 + 记忆 ===")

    # 进行工具调用测试
    print("\n--- 对话测试 ---")
    response = agent.act("我现在在哪里？那里的天气怎么样？")
    print(f"\n最终响应: {response}")

    # 查看记忆内容
    print(f"\n--- 记忆内容 ({len(agent.memory)} 条消息) ---")
    for msg in agent.memory.get_all():
        print(f"  [{msg.role}]: {msg.content[:80]}...")