import os
import sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import LLMClient
from tools import ToolRegistry
from memory import Memory, ConversationMemory, Message


class Agent:
    """支持工具调用和记忆的Agent"""

    def __init__(
        self,
        name: str,
        llm: LLMClient,
        system_prompt: str = None,
        tool_registry: ToolRegistry = None,
        memory: Memory = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt or "你是一个专业的助手"
        self.tool_registry = tool_registry
        # 默认使用会话记忆
        self.memory = memory if memory is not None else ConversationMemory()

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
        messages = self.memory.build_messages(self.system_prompt, input)

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

    # 创建带工具的Agent
    agent = Agent(
        name="天气助手",
        llm=llm,
        system_prompt="你是一个天气助手，可以帮助用户查询天气信息。当用户询问天气时，先查询位置，再查询天气。",
        tool_registry=registry
    )

    print("=== 测试 Agent 工具调用 + 记忆 ===")

    # 第一次对话（使用工具查询天气）
    print("\n--- 第一次对话 ---")
    response1 = agent.act("我现在在哪里？那里的天气怎么样？")
    print(f"\n最终响应: {response1}")

    # 第二次对话（应该记得之前的查询结果）
    print("\n--- 第二次对话 ---")
    response2 = agent.act("你还记得我刚才查询的城市和天气吗？")
    print(f"\n最终响应: {response2}")

    # 查看记忆内容
    print(f"\n--- 记忆内容 ({len(agent.memory)} 条消息) ---")
    for msg in agent.memory.get_all():
        print(f"  [{msg.role}]: {msg.content[:80]}...")