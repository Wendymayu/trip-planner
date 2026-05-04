## 工具调用实现

Agent工具调用能力已成功实现。修改了三个文件：

1. tools.py
添加 ToolSchema 数据类，存储工具定义和参数schema
增强 ToolRegistry：
register() - 支持显式定义描述和参数
get_openai_tools() - 生成 OpenAI function calling 格式
execute() - 执行工具并返回结果
2. llm.py
添加 chat() 方法，支持传入 messages 和 tools 参数
返回完整的 OpenAI 响应对象，包含 tool_calls 信息
3. agent.py
重写 act() 方法实现工具调用循环：
调用 LLM，传入工具 schema
检查 tool_calls，执行对应工具
将工具结果作为 role: "tool" 消息返回
循环直到无工具调用或达到最大迭代次数
测试验证了完整的多轮工具调用流程，Agent 能够智能地先查询位置、再查询天气、最后生成回答。

