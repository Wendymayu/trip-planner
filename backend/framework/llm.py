import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

from openai import OpenAI
from typing import List, Dict, Any, Optional


class LLMClient:
    """LLM客户端，支持工具调用"""

    def __init__(self, **kwargs):
        self.model_name = os.getenv("LLM_MODEL_NAME") or "glm-5"
        self.api_key = os.getenv("LLM_API_KEY") or "sk-c224e4bdd2d04af593a86ebab175f427"
        self.base_url = os.getenv("LLM_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens')
        self.timeout = kwargs.get('timeout', 60)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def think(self, prompt: str, system_prompt: str = "你是一个专业的助手") -> str:
        """简单的思考方法，不使用工具"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLMClient.think() error: {e}")
            return f"LLM调用失败: {str(e)}"

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto"
    ) -> Any:
        """
        支持工具调用的聊天方法

        Args:
            messages: 消息列表，每条消息包含 role 和 content
            tools: 工具列表 (OpenAI function calling 格式)
            tool_choice: 工具选择策略 ("auto", "none", "required" 或指定工具)

        Returns:
            OpenAI ChatCompletion 响应对象
        """
        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
            }

            if self.max_tokens:
                params["max_tokens"] = self.max_tokens

            if tools:
                params["tools"] = tools
                params["tool_choice"] = tool_choice

            response = self.client.chat.completions.create(**params)
            return response

        except Exception as e:
            print(f"LLMClient.chat() error: {e}")
            raise


if __name__ == "__main__":
    load_dotenv()

    # 测试基本思考功能
    llm = LLMClient()
    input_text = "今天南京天气如何"
    print(f"输入: {input_text}")
    result = llm.think(input_text)
    print(f"响应: {result}")

    # 测试带工具的chat功能
    print("\n=== 测试工具调用 ===")
    messages = [{"role": "user", "content": "北京今天天气怎么样？"}]
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    }]

    response = llm.chat(messages, tools=tools)
    message = response.choices[0].message

    if message.tool_calls:
        print(f"模型请求调用工具: {message.tool_calls}")
        for tool_call in message.tool_calls:
            print(f"  工具名: {tool_call.function.name}")
            print(f"  参数: {tool_call.function.arguments}")
    else:
        print(f"模型直接响应: {message.content}")
