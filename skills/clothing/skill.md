---
name: clothing
description: 根据天气和活动推荐穿搭（仅用于穿衣建议场景）
user-invocable: true
license: MIT
metadata:
  version: 1.0.0
  author: Trip Planner Team
  tags: [clothing, travel, weather, recommendation]
---

# Clothing Recommendation Skill

## Description
根据给定地点、天气和温度，为用户生成结构化穿搭建议。

---

## When to use
- 用户询问穿什么衣服
- 用户提供天气/温度并希望获得穿搭建议
- 旅行、出行、日常穿衣规划

## When NOT to use
- 用户未涉及穿衣/天气
- 用户在问时尚搭配（不基于天气）
- 用户问题是情绪/闲聊

## Parameters

- location (string, required): 目的地名称
- weather (string, required): 天气状况（晴、多云、雨、雪等）
- temperature (integer, optional): 温度（摄氏度）
- activity (string, optional): 活动类型（日常、运动、商务等）

## Returns

```json
{
  "location": "string",
  "weather": "string",
  "temperature": "integer",
  "recommendation": {
    "top": "string",
    "bottom": "string",
    "outerwear": "string",
    "accessories": ["string"],
    "tips": ["string"]
  }
}
```

## Example

```python
result = skill.execute(
    location="北京",
    weather="晴",
    temperature=25,
    activity="日常"
)
```

## Notes

- 根据温度区间推荐不同厚度的衣物
- 雨雪天气会推荐雨具和防滑鞋
- 可根据活动类型调整穿搭风格
