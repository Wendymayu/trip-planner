"""Skill 加载器（只管理开源 Skill）

所有 Skill 来自开源 skill.md 格式：
- 从 skills 目录批量加载
- 支持延迟加载（先加载元数据，执行时再加载实现）
- 可转换为 Tool 格式（早绑定）
"""

import sys
import os
from pathlib import Path
from typing import List

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

from framework.skill.loader import SkillLoader


class SkillRegistry:
    """Skill 加载器（支持转换为 Tool）

    使用示例:
        from framework.skill import SkillRegistry
        from framework.tools import ToolRegistry

        # 加载 Skills
        skill_registry = SkillRegistry()
        skill_registry.load_from_directory("./skills")

        # 转换为 Tools（早绑定）
        tool_registry = ToolRegistry()
        skill_registry.register_to_tool_registry(tool_registry)

        # 统一通过 ToolRegistry 执行
        result = tool_registry.execute("clothing", {"location": "北京", "weather": "晴"})
    """

    def __init__(self):
        self._skills = {}
        self._loader = SkillLoader()

    def load_from_directory(self, directory: str) -> int:
        """批量加载 Skill 目录

        Args:
            directory: Skill 目录路径（包含多个 skill 文件夹）

        Returns:
            成功加载的 Skill 数量
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {directory}")

        count = 0
        for subfolder in dir_path.iterdir():
            if subfolder.is_dir():
                try:
                    skill = self._loader.load_metadata(str(subfolder))
                    if skill:
                        self._skills[skill.name] = skill
                        count += 1
                except Exception as e:
                    print(f"[失败] 加载 {subfolder.name}: {e}")

        return count

    def register_to_tool(self, tool_registry) -> int:
        """将所有 Skill 注册为 Tool（早绑定）

        Args:
            tool_registry: ToolRegistry 实例

        Returns:
            成功注册的数量
        """
        count = 0
        for skill in self._skills.values():
            tool_registry.register_skill(skill)
            count += 1
        return count

    def get(self, name: str):
        """获取 Skill"""
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """列出所有 Skill 名称"""
        return list(self._skills.keys())

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        return name in self._skills


if __name__ == "__main__":
    print("=== 测试 SkillRegistry ===\n")

    registry = SkillRegistry()

    # 从 skills 目录加载
    skills_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "skills")
    count = registry.load_from_directory(skills_dir)
    print(f"成功加载 {count} 个 Skill\n")

    # 列出所有 Skill
    print("--- Skill 列表 ---")
    for name in registry.list_skills():
        skill = registry.get(name)
        print(f"  - {name}: {skill.description}")

    # 转换为 Tool 并执行
    print("\n--- 转换为 Tool 并执行 ---")
    from framework.tools import ToolRegistry
    tool_registry = ToolRegistry()
    registry.register_to_tool(tool_registry)
    print(f"成功注册 {len(tool_registry.tools)} 个 Tool\n")

    # 执行
    result = tool_registry.execute("clothing", {"location": "北京", "weather": "晴", "temperature": 30})
    print(f"clothing 结果: {result}")
