"""Clothing Skill 实现

根据地点和天气推荐穿衣搭配
"""

def execute(
    location: str,
    weather: str,
    temperature: int = None,
    activity: str = "日常"
) -> dict:
    """推荐穿衣搭配

    Args:
        location: 目的地名称
        weather: 天气状况（晴、多云、雨、雪等）
        temperature: 温度（摄氏度）
        activity: 活动类型（日常、运动、商务等）

    Returns:
        穿衣推荐字典
    """
    # 根据温度推荐衣物
    top = ""
    bottom = ""
    outerwear = ""
    accessories = []
    tips = []

    # 温度区间判断（如果没有温度，根据天气推测）
    temp = temperature or _estimate_temp(weather)

    if temp >= 30:
        # 炎热
        top = "短袖T恤或薄衬衫"
        bottom = "短裤或薄裙"
        outerwear = "无需外套"
        accessories = ["遮阳帽", "太阳镜"]
        tips.append("注意防晒，涂抹防晒霜")
        tips.append("选择透气吸汗的面料")
    elif temp >= 25:
        # 温暖
        top = "薄T恤或衬衫"
        bottom = "长裤或裙"
        outerwear = "薄外套（备用）"
        accessories = ["遮阳帽"]
        tips.append("早晚温差可能较大，备一件薄外套")
    elif temp >= 20:
        # 舒适
        top = "长袖T恤或薄毛衣"
        bottom = "长裤"
        outerwear = "薄外套或开衫"
        accessories = []
        tips.append("温度适宜，穿搭自由度高")
    elif temp >= 15:
        # 微凉
        top = "毛衣或卫衣"
        bottom = "长裤"
        outerwear = "夹克或风衣"
        accessories = []
        tips.append("建议穿长袖并备外套")
    elif temp >= 10:
        # 较冷
        top = "厚毛衣或保暖内衣+毛衣"
        bottom = "厚长裤"
        outerwear = "厚外套或棉服"
        accessories = ["围巾"]
        tips.append("注意保暖，避免受凉")
    elif temp >= 5:
        # 寒冷
        top = "保暖内衣+毛衣+羽绒服内胆"
        bottom = "厚长裤+保暖裤"
        outerwear = "羽绒服或厚棉服"
        accessories = ["围巾", "手套", "帽子"]
        tips.append("寒冷天气，注意全面保暖")
    else:
        # 极寒
        top = "保暖内衣+厚毛衣+羽绒服"
        bottom = "加绒裤+保暖裤"
        outerwear = "厚羽绒服或棉服"
        accessories = ["围巾", "手套", "厚帽子", "口罩"]
        tips.append("极寒天气，尽量减少户外活动")
        tips.append("穿防滑保暖鞋")

    # 根据天气状况调整
    if weather in ["雨", "小雨", "大雨", "暴雨"]:
        accessories.append("雨伞")
        accessories.append("防水鞋或雨靴")
        tips.append("雨天注意防滑，穿防水鞋")
        if outerwear == "无需外套":
            outerwear = "防水外套或雨衣"
    elif weather in ["雪", "小雪", "大雪"]:
        accessories.append("防滑靴")
        tips.append("雪天注意保暖和防滑")
        tips.append("穿防水保暖鞋")
    elif weather in ["晴", "晴天"]:
        if temp >= 25:
            accessories.append("太阳镜")
            tips.append("晴天紫外线强，注意防晒")
    elif weather in ["多云", "阴"]:
        tips.append("天气可能变化，建议备外套")

    # 根据活动类型调整
    if activity == "运动":
        tips.append("运动时选择透气舒适的运动装")
        if "外套" in outerwear:
            tips.append("运动时可脱掉外套，运动后及时穿上")
    elif activity == "商务":
        if temp >= 20:
            top = "衬衫或薄西装"
            outerwear = "西装外套"
            tips.append("商务场合建议正装")
        else:
            top = "衬衫+西装内胆"
            outerwear = "厚西装或商务大衣"
            tips.append("商务场合注意保暖与得体兼顾")
    elif activity == "户外":
        tips.append("户外活动建议穿舒适耐穿的衣服")
        tips.append("备好防晒或保暖用品")

    # 去重
    accessories = list(set(accessories))
    tips = list(set(tips))

    return {
        "location": location,
        "weather": weather,
        "temperature": temp,
        "activity": activity,
        "recommendation": {
            "top": top,
            "bottom": bottom,
            "outerwear": outerwear,
            "accessories": accessories,
            "tips": tips
        }
    }


def _estimate_temp(weather: str) -> int:
    """根据天气状况估计温度"""
    temp_map = {
        "晴": 25,
        "晴天": 25,
        "多云": 20,
        "阴": 18,
        "雨": 15,
        "小雨": 15,
        "大雨": 12,
        "暴雨": 10,
        "雪": 0,
        "小雪": 2,
        "大雪": -5,
    }
    return temp_map.get(weather, 20)


if __name__ == "__main__":
    # 测试
    result = execute(location="北京", weather="晴", temperature=30)
    print(f"炎热天气: {result}\n")

    result = execute(location="上海", weather="雨", temperature=15)
    print(f"雨天微凉: {result}\n")

    result = execute(location="哈尔滨", weather="雪", temperature=-10)
    print(f"极寒雪天: {result}\n")