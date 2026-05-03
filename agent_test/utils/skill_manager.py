# utils/skill_manager.py
"""
Hermes 风格 Skill 管理
从 skills/xxx/SKILL.md 加载所有技能
支持 LLM 自主选择或规则路由
"""
import os
import re
from importlib import resources

SKILL_ROOT = resources.files('agent_test') / 'skills'

def load_all_skills_from_md() -> dict:
    """
    遍历 skills 目录，加载所有 SKILL.md 并解析为 Skill 结构
    返回 {skill_id: {...}}
    """
    skills = {}

    for skill_id in os.listdir(SKILL_ROOT):
        skill_dir = os.path.join(SKILL_ROOT, skill_id)
        if not os.path.isdir(skill_dir):
            continue

        md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(md_path):
            continue

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 简单字段解析
        name = extract(md_path, content, r"Name:\s*(.+)")
        desc = extract(md_path, content, r"Description:\s*(.+)")
        tools_str = extract(md_path, content, r"Tools:\s(.+)", warn=False)
        tools = [t.strip() for t in tools_str.split(",")] if tools_str else []

        skills[skill_id] = {
            "name": name,
            "description": desc,
            "tools": tools,
            "prompt": content,  # 全文作为技能 Prompt
            "skill_id": skill_id
        }

    return skills

def extract(path, content, pattern, warn=True):
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if warn:
        print(f"[警告] {path} 未匹配字段: {pattern}")
    return ""

# 全局加载一次
SKILLS = load_all_skills_from_md()

def get_available_skills_summary() -> str:
    """
    生成可用技能的简洁描述，用于 LLM 选择
    """
    lines = []
    for sid, skill in SKILLS.items():
        lines.append(f"- **{sid}**: {skill['name']} —— {skill['description']}")
    return "\n".join(lines)

def get_skill(skill_id: str):
    return SKILLS.get(skill_id, SKILLS.get("pipeline_master"))
