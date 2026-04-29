import sys
import io

# Windows控制台UTF-8编码支持
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Trip Planner Backend API",
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}

from app.agents.trip_planner_agent import get_trip_planner_agent
from app.models.schemas import TripRequest
import json
if __name__ == "__main__":
    # 测试多智能体系统
    agent = get_trip_planner_agent()
    test_request = TripRequest(
        city="北京",
        start_date="2026-05-01",
        end_date="2026-05-05",
        travel_days=5,
        transportation="公共交通",
        accommodation="经济型酒店",
        preferences=["历史文化", "公园"],
        free_text_input="我喜欢安静的地方,不喜欢太商业化的景点。"
    )
    trip_plan = agent.plan_trip(test_request)
    print(json.dumps(trip_plan.model_dump(), ensure_ascii=False, indent=2))


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
