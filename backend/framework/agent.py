import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import LLMClient
from tools import ToolRegistry

class Agent:
    def __init__(self, name: str,  llm:LLMClient, system_prompt:str=None, tool_registry:ToolRegistry=None):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry

    def act(self, input: str) -> str:
        # 这里可以添加一些预处理逻辑，比如输入清洗、上下文管理等
        response = self.llm.think(input)
        # 这里可以添加一些后处理逻辑，比如结果解析、格式化等
        return response
    
if __name__ == "__main__":
    llm = LLMClient()
    agent = Agent("测试", llm)
    response = agent.act("你好")
    print(f"agent says: {response}")