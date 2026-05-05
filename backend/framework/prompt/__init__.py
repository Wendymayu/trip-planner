"""提示词模板模块

支持可参数化的系统提示词。

使用示例:
    from framework.prompt import PromptTemplate

    template = PromptTemplate(
        name="weather",
        template="你是{{city}}的天气助手，任务：{{task}}",
        defaults={"task": "查询天气"}
    )
    prompt = template.render(city="北京")
"""

from .templates import PromptTemplate

__all__ = ["PromptTemplate"]
