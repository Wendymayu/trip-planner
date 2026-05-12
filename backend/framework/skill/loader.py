"""Skill 加载器（渐进式加载）

支持标准开源 Skill 格式：
- YAML frontmatter 定义元数据
- Markdown body 定义详细说明
- 渐进式加载：先加载元数据，执行时才加载实现

使用示例:
    from framework.skill import SkillLoader

    # 加载元数据（快速）
    loader = SkillLoader()
    skill = loader.load_metadata("./skills/weather")

    # 执行时才加载实现（延迟加载）
    result = skill.execute(city="北京")
"""

import os
import sys
import re
import yaml
import importlib.util
from typing import Dict, Any, Optional, List
from pathlib import Path

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)

from framework.skill.base import Skill, SkillResult


class MetadataSkill(Skill):
    """元数据 Skill（延迟加载实现）

    只包含元数据，实现代码在首次执行时才加载。
    适合批量加载大量 Skill 的场景。
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        metadata: Dict[str, Any],
        implementation_path: str = None
    ):
        super().__init__()
        self.name = name
        self.description = description
        self.parameters = parameters
        self._metadata = metadata
        self._implementation_path = implementation_path
        self._implementation = None  # 延迟加载
        self._loaded = False

    def _load_implementation(self):
        """延迟加载实现代码"""
        if self._loaded or not self._implementation_path:
            return

        if not os.path.exists(self._implementation_path):
            self._loaded = True
            return

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(
            f"skill_{self.name}",
            self._implementation_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找执行函数
        if hasattr(module, 'execute'):
            self._implementation = getattr(module, 'execute')
        elif hasattr(module, self.name):
            self._implementation = getattr(module, self.name)

        self._loaded = True

    def execute(self, **kwargs) -> SkillResult:
        """执行 Skill（延迟加载实现）"""
        # 首次执行时加载实现
        if not self._loaded:
            self._load_implementation()

        # 没有实现
        if not self._implementation:
            return SkillResult(
                success=False,
                output=None,
                error=f"No implementation found for skill '{self.name}'"
            )

        try:
            # 执行函数
            result = self._implementation(**kwargs)

            # 包装为 SkillResult
            if isinstance(result, SkillResult):
                return result

            return SkillResult(success=True, output=result)

        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e)
            )


class SkillLoader:
    """Skill 加载器（渐进式）

    使用示例:
        loader = SkillLoader()

        # 方式1：只加载元数据（快速）
        skill = loader.load_metadata("./skills/weather")

        # 方式2：加载元数据 + 实现（完整）
        skill = loader.load("./skills/weather")

        # 方式3：批量加载元数据
        skills = loader.load_metadata_from_directory("./skills")
    """

    def parse_skill_md(self, filepath: str) -> Dict[str, Any]:
        """解析 skill.md 文件

        Args:
            filepath: skill.md 文件路径

        Returns:
            {
                "name": str,
                "description": str,
                "parameters": dict,
                "metadata": dict,
                "content": str  # Markdown body
            }
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML frontmatter
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                metadata = yaml.safe_load(yaml_content) or {}
                body = parts[2].strip()
            else:
                body = content
        else:
            body = content

        # 提取参数定义
        parameters = self._parse_parameters(body)

        return {
            "name": metadata.get("name", Path(filepath).parent.name),
            "description": metadata.get("description", self._extract_first_paragraph(body)),
            "parameters": parameters,
            "metadata": metadata,
            "content": body
        }

    def _parse_parameters(self, body: str) -> Dict[str, Any]:
        """从 Markdown body 解析参数定义

        Args:
            body: Markdown 内容

        Returns:
            OpenAI Function Calling 格式的 parameters
        """
        properties = {}
        required = []

        # 匹配参数行
        # 格式: - param_name (type, required/optional): description
        pattern = r'-\s+`?(\w+)`?\s*\((\w+)(?:,\s*(required|optional))?\)\s*:\s*(.+)'
        matches = re.findall(pattern, body, re.MULTILINE)

        type_map = {
            'string': 'string',
            'str': 'string',
            'integer': 'integer',
            'int': 'integer',
            'number': 'number',
            'float': 'number',
            'boolean': 'boolean',
            'bool': 'boolean',
            'array': 'array',
            'list': 'array',
            'object': 'object',
            'dict': 'object',
        }

        for param_name, param_type, requirement, desc in matches:
            json_type = type_map.get(param_type.lower(), 'string')

            properties[param_name] = {
                "type": json_type,
                "description": desc.strip()
            }

            if requirement and 'required' in requirement.lower():
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def _extract_first_paragraph(self, body: str) -> str:
        """提取第一个段落作为描述"""
        lines = body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line
        return ""

    def load_metadata(self, skill_folder: str) -> Optional[MetadataSkill]:
        """只加载元数据（快速，延迟加载实现）

        Args:
            skill_folder: Skill 文件夹路径

        Returns:
            MetadataSkill 实例
        """
        folder_path = Path(skill_folder)

        if not folder_path.exists():
            raise ValueError(f"Skill folder not found: {skill_folder}")

        # 查找 skill.md
        skill_md = folder_path / "skill.md"
        if not skill_md.exists():
            raise ValueError(f"skill.md not found in {skill_folder}")

        # 解析元数据
        skill_info = self.parse_skill_md(str(skill_md))

        # 查找实现文件（但不加载）
        possible_files = [
            folder_path / "skill.py",
            folder_path / f"{skill_info['name']}.py",
            folder_path / "main.py",
        ]

        implementation_path = None
        for py_file in possible_files:
            if py_file.exists():
                implementation_path = str(py_file)
                break

        # 创建 MetadataSkill
        return MetadataSkill(
            name=skill_info['name'],
            description=skill_info['description'],
            parameters=skill_info['parameters'],
            metadata=skill_info['metadata'],
            implementation_path=implementation_path
        )

    def load(self, skill_folder: str) -> Optional[MetadataSkill]:
        """加载 Skill（加载元数据 + 立即加载实现）

        Args:
            skill_folder: Skill 文件夹路径

        Returns:
            MetadataSkill 实例（已加载实现）
        """
        skill = self.load_metadata(skill_folder)
        if skill:
            skill._load_implementation()
        return skill

    def load_metadata_from_directory(self, directory: str) -> List[MetadataSkill]:
        """批量加载元数据（快速，适合大量 Skill）

        Args:
            directory: Skill 目录路径

        Returns:
            MetadataSkill 列表
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise ValueError(f"Directory not found: {directory}")

        skills = []

        for subfolder in dir_path.iterdir():
            if subfolder.is_dir():
                try:
                    skill = self.load_metadata(str(subfolder))
                    skills.append(skill)
                    print(f"[元数据] {skill.name} - {skill.description}")
                except Exception as e:
                    print(f"[失败] {subfolder.name}: {e}")

        return skills

    def load_from_directory(self, directory: str) -> List[MetadataSkill]:
        """批量加载（元数据 + 实现）

        Args:
            directory: Skill 目录路径

        Returns:
            MetadataSkill 列表（已加载实现）
        """
        skills = self.load_metadata_from_directory(directory)
        for skill in skills:
            skill._load_implementation()
        return skills


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')

    print("=== 测试渐进式 SkillLoader ===\n")

    # 测试解析 skill.md
    loader = SkillLoader()

    print("--- 测试1: 只加载元数据（快速） ---")
    skill = loader.load_metadata("./skills/weather")
    print(f"Skill 名称: {skill.name}")
    print(f"描述: {skill.description}")
    print(f"参数: {skill.parameters}")
    print(f"实现已加载: {skill._loaded}")

    print("\n--- 测试2: 首次执行时加载实现 ---")
    result = skill.execute(city="北京")
    print(f"执行结果: {result.to_dict()}")
    print(f"实现已加载: {skill._loaded}")

    print("\n--- 测试3: 批量加载元数据 ---")
    skills = loader.load_metadata_from_directory("./skills")
    print(f"加载了 {len(skills)} 个 Skill（仅元数据）")

    print("\n--- 测试4: 执行多个 Skill ---")
    for s in skills:
        if s.name == "weather":
            result = s.execute(city="上海")
            print(f"Weather: {result.to_dict()}")
        elif s.name == "location":
            result = s.execute(city="广州")
            print(f"Location: {result.to_dict()}")
