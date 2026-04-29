"""多智能体旅行规划系统"""

import json
from typing import Dict, Any, List
from hello_agents import SimpleAgent
from hello_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings

# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点分析专家。根据搜索到的景点数据,为用户筛选和推荐合适的景点。

你需要从搜索结果中:
1. 筛选出最值得游览的景点
2. 提供景点的简要描述
3. 建议游览时长
4. 按优先级排序

返回格式:
景点名称 | 地址 | 类型 | 建议游览时长 | 简介
"""

WEATHER_AGENT_PROMPT = """你是天气分析专家。根据天气数据,为旅行者提供穿衣和活动建议。

分析天气信息并给出:
1. 天气概况
2. 适宜的活动类型
3. 穿衣建议
4. 是否需要带雨具等

返回简洁的天气摘要和建议。
"""

HOTEL_AGENT_PROMPT = """你是酒店分析专家。根据搜索到的酒店数据,为用户推荐合适的住宿。

从搜索结果中:
1. 筛选出性价比高的酒店
2. 按价格、位置、评分排序
3. 提供简要评价

返回格式:
酒店名称 | 地址 | 价格范围 | 特点
"""

PLANNER_AGENT_PROMPT = """你是行程规划专家。根据景点、天气和酒店信息,生成详细的旅行计划。

请严格按照以下JSON格式返回旅行计划:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

重要:
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 景点坐标使用提供的数据
4. 必须包含预算信息
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 开始初始化多智能体旅行规划系统...")

        try:
            settings = get_settings()
            self.llm = get_llm()
            self.settings = settings

            # 创建MCP工具客户端
            print("  - 创建MCP工具客户端...")
            import shutil
            amap_cmd = shutil.which("amap-mcp-server") or "amap-mcp-server"
            print(f"  - MCP服务器命令: {amap_cmd}")
            self.mcp_tool = MCPTool(
                name="amap",
                description="高德地图服务",
                server_command=[amap_cmd],
                env={"AMAP_MAPS_API_KEY": settings.amap_maps_api_key},
                auto_expand=True
            )
            self.mcp_tool.expandable = True

            # 创建分析型Agent(不需要工具,只处理数据)
            print("  - 创建景点分析Agent...")
            self.attraction_agent = SimpleAgent(
                name="景点分析专家",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT
            )

            print("  - 创建天气分析Agent...")
            self.weather_agent = SimpleAgent(
                name="天气分析专家",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT
            )

            print("  - 创建酒店分析Agent...")
            self.hotel_agent = SimpleAgent(
                name="酒店分析专家",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT
            )

            print("  - 创建行程规划Agent...")
            self.planner_agent = SimpleAgent(
                name="行程规划专家",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            print(f"✅ 多智能体系统初始化成功")

        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """直接调用MCP工具"""
        try:
            # run方法需要 tool_name 和 arguments
            params = {"tool_name": tool_name, "arguments": arguments}
            result = self.mcp_tool.run(params)
            return str(result) if result else "无返回结果"
        except Exception as e:
            print(f"⚠️ MCP工具调用失败: {str(e)}")
            return f"工具调用失败: {str(e)}"

    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'='*60}\n")

            # 步骤1: 直接调用MCP搜索景点
            print("📍 步骤1: 搜索景点...")
            keywords = request.preferences[0] if request.preferences else "景点"
            attraction_data = self._call_mcp_tool(
                "maps_text_search",
                {"keywords": keywords, "city": request.city}
            )
            print(f"景点原始数据: {attraction_data[:200] if attraction_data else '无数据'}...\n")

            # 让Agent分析景点数据
            if attraction_data and "失败" not in attraction_data:
                attraction_response = self.attraction_agent.run(
                    f"以下是{request.city}的景点搜索结果,请分析和推荐:\n{attraction_data}"
                )
            else:
                attraction_response = f"景点搜索失败,请根据{request.city}的常见景点进行推荐"

            # 步骤2: 直接调用MCP查询天气
            print("🌤️  步骤2: 查询天气...")
            weather_data = self._call_mcp_tool(
                "maps_weather",
                {"city": request.city}
            )
            print(f"天气原始数据: {weather_data[:200] if weather_data else '无数据'}...\n")

            if weather_data and "失败" not in weather_data:
                weather_response = self.weather_agent.run(
                    f"以下是{request.city}的天气数据,请分析和给出建议:\n{weather_data}"
                )
            else:
                weather_response = "天气查询失败,请假设适宜天气进行规划"

            # 步骤3: 直接调用MCP搜索酒店
            print("🏨 步骤3: 搜索酒店...")
            hotel_data = self._call_mcp_tool(
                "maps_text_search",
                {"keywords": request.accommodation + "酒店", "city": request.city}
            )
            print(f"酒店原始数据: {hotel_data[:200] if hotel_data else '无数据'}...\n")

            if hotel_data and "失败" not in hotel_data:
                hotel_response = self.hotel_agent.run(
                    f"以下是{request.city}的酒店搜索结果,请分析和推荐:\n{hotel_data}"
                )
            else:
                hotel_response = f"酒店搜索失败,请根据{request.city}的常见{request.accommodation}酒店进行推荐"

            # 步骤4: 行程规划Agent整合信息生成计划
            print("📋 步骤4: 生成行程计划...")
            planner_query = self._build_planner_query(
                request, attraction_response, weather_response, hotel_response,
                attraction_data, weather_data, hotel_data
            )
            planner_response = self.planner_agent.run(planner_query)
            print(f"行程规划结果: {planner_response[:300]}...\n")

            # 解析最终计划
            trip_plan = self._parse_response(planner_response, request)

            print(f"{'='*60}")
            print(f"✅ 旅行计划生成完成!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ 生成旅行计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)

    def _build_planner_query(
        self,
        request: TripRequest,
        attraction_summary: str,
        weather_summary: str,
        hotel_summary: str,
        attraction_raw: str = "",
        weather_raw: str = "",
        hotel_raw: str = ""
    ) -> str:
        """构建行程规划查询"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天旅行计划:

**基本信息:**
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}天
- 交通方式: {request.transportation}
- 住宿: {request.accommodation}
- 偏好: {', '.join(request.preferences) if request.preferences else '无'}

**景点分析:**
{attraction_summary}

**景点原始数据(用于获取坐标):**
{attraction_raw[:1000] if attraction_raw else '无'}

**天气分析:**
{weather_summary}

**酒店分析:**
{hotel_summary}

**要求:**
1. 每天安排2-3个景点
2. 每天必须包含早中晚三餐
3. 每天推荐一个酒店
4. 返回完整的JSON格式数据
5. 景点坐标使用原始数据中的真实坐标
"""
        if request.free_text_input:
            query += f"\n**额外要求:** {request.free_text_input}"

        return query

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """解析Agent响应"""
        try:
            # 尝试从响应中提取JSON
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")

            # 解析JSON
            data = json.loads(json_str)
            trip_plan = TripPlan(**data)
            return trip_plan

        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            print(f"   将使用备用方案生成计划")
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta

        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"第{i+1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city}景点{j+1}",
                        address=f"{request.city}市",
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"这是{request.city}的著名景点",
                        category="景点"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"第{i+1}天早餐", description="当地特色早餐"),
                    Meal(type="lunch", name=f"第{i+1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i+1}天晚餐", description="晚餐推荐")
                ]
            )
            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程,建议提前查看各景点的开放时间。"
        )


# 全局多智能体系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner