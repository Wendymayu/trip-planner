import sys

sys.stdout.reconfigure(encoding="utf-8")


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func):
        self.tools[name] = func

    def get_tool(self, name: str) -> callable:
        return self.tools.get(name)

# 查询当前地理位置
def query_location() -> str:
    # 这里可以调用第三方GPS定位API获取当前位置信息
    return {"city": "北京", "latitude": 39.9042, "longitude": 116.4074}

# 查询天气工具
def query_weather(city: str, date: str = None) -> str:
    # 这里可以调用第三方天气API获取天气信息
    return f"{city}的天气是晴朗，温度25度。"


if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register("query_location", query_location)
    registry.register("query_weather", query_weather)

    location_tool = registry.get_tool("query_location")
    if location_tool:
        location = location_tool()
        print(location)
    city = location.get("city", "未知")
        
    
    tool = registry.get_tool("query_weather")
    if tool:
        result = tool(city)
        print(result)
