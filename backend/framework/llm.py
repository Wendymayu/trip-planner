import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

from openai import OpenAI


class LLMClient():
    def __init__(self, **kwargs):
        self.model_name = os.getenv("LLM_MODEL_NAME") or "glm-5"
        self.api_key = os.getenv("LLM_API_KEY") or "sk-c224e4bdd2d04af593a86ebab175f427"
        self.base_url = os.getenv("LLM_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens')
        self.timeout = kwargs.get('timeout', 60)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def think(self, prompt: str) -> str:
        try: 
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "你是一个专业的天气分析助手"},{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLMClient.think() error: {e}")

if __name__ =="__main__":
    load_dotenv()  # 加载环境变量
    llmClient = LLMClient()
    input = "今天南京天气如何"
    print(f"输入: {input}")
    result = llmClient.think(input)
    print(result)