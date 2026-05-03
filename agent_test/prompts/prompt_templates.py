# prompts/prompt_templates.py
"""
智能体标准化 Prompt 工程 + 短期记忆支持
系统提示 + 格式约束 + 任务指令 = 稳定输出
"""

# 身份与规则（核心约束）
SYSTEM_PROMPT = """
你是【学术数据智能体】，严格遵守：
1. 专业、简洁、不闲聊
2. 仅处理CSV数据分析、绘图、计算
3. 严格按格式输出
4. 基于历史对话回答，保持上下文连贯
"""

# 输出格式约束
FORMAT_PROMPT = """
输出要求：
- 纯文本，无markdown
- 分点清晰
- 不使用特殊符号
"""

# 新增：支持历史对话的Prompt模板
TASK_TEMPLATE_WITH_MEMORY = """
历史对话：
{history}

用户当前请求：{user_input}
"""

def build_prompt_with_memory(user_input: str, history_text: str) -> str:
    """
    构建带短期记忆的完整Prompt
    """
    return f"{SYSTEM_PROMPT}\n{FORMAT_PROMPT}\n{TASK_TEMPLATE_WITH_MEMORY.format(history=history_text, user_input=user_input)}"

# ------------------------------
# Hermes Skill Prompt（从 MD 加载）
# ------------------------------
SKILL_PROMPT_TEMPLATE = """
===== 系统身份与技能说明 =====
{skill_prompt}
============================

历史对话：
{history}

用户指令：{user_input}

请严格按照你的技能规则完成任务。
"""

def build_skill_prompt(skill_info, user_input, history_text):
    return SKILL_PROMPT_TEMPLATE.format(
        skill_prompt=skill_info["prompt"],
        history=history_text,
        user_input=user_input
    )

# ------------------------------
# 技能选择 Prompt（新增）
# ------------------------------
SKILL_SELECTION_TEMPLATE = """你是一个智能任务路由器。请根据用户输入，从以下可用技能中选择最合适的一个。

可用技能列表：
{skills_summary}

用户输入：
"{user_input}"

请仅返回一个 JSON 对象，格式如下：
{{"skill_id": "data_analyzer", "reason": "简要理由"}}

确保 skill_id 是上述列表中的有效值。"""

def build_skill_selection_prompt(user_input: str, skills_summary: str) -> str:
    """
    构造让 LLM 选择技能的 prompt
    :param user_input: 用户原始输入
    :param skills_summary: 由 skill_manager 生成的技能摘要字符串
    """
    return SKILL_SELECTION_TEMPLATE.format(
        skills_summary=skills_summary,
        user_input=user_input
    )

# ------------------------------
# 模块6 新增：带长期记忆的技能执行 Prompt
# ------------------------------
SKILL_WITH_LONG_MEMORY_TEMPLATE = """
===== 系统身份 =====
你是：{skill_name}

===== 长期记忆（技能规范）=====
{long_memory}

===== 历史对话 =====
{history}

===== 用户指令 =====
{user_input}

===== 工具执行结果 =====
{tool_result}

请严格遵循技能规则完成任务，并判断任务是否完成。
返回严格 JSON 格式：
{{
    "final_answer": "最终回答",
    "need_more_tool": false,
    "is_done": true
}}
"""

def build_skill_with_long_memory_prompt(
    skill_info: dict,
    user_input: str,
    history_text: str,
    long_memory: str,
    tool_result: str
):
    return SKILL_WITH_LONG_MEMORY_TEMPLATE.format(
        skill_name=skill_info["name"],
        long_memory=long_memory,
        history=history_text,
        user_input=user_input,
        tool_result=tool_result
    )

# ==============================
# 文件路径提取 Prompt（已存在，无需修改）
# ==============================
FILE_PATH_EXTRACTION_TEMPLATE = """从以下用户请求中提取所有提到的CSV或数据文件路径，仅返回路径字符串（多个用逗号分隔）。如果未提及任何文件，返回空字符串。不要解释。

用户请求：{user_input}"""

def build_file_path_extraction_prompt(user_input: str) -> str:
    return FILE_PATH_EXTRACTION_TEMPLATE.format(user_input=user_input)


# ==============================
# 沙箱代码生成 Prompt（已存在，但可微调）
# ==============================
CODE_GENERATION_TEMPLATE = """你是一个严格遵循技能规则的智能体。
当前技能：{skill_name}
技能描述：{skill_description}
技能规则全文：
{skill_prompt}

用户原始需求：{user_original_input}
当前步骤具体任务：{current_action}
已知文件路径：{file_paths}

【已完成步骤的上下文（可从中提取真实特征名、数值等）】
{recent_history}

请生成一段可直接执行的 Python 代码。要求：
- 仅使用标准库和已安装的 pandas, numpy, matplotlib, sklearn 等，自行 import
- 所有关键结果用 print() 输出
- 若任务涉及绘图，请使用 matplotlib，设置 Times New Roman 字体、300 dpi，并打印保存路径
- **绝对禁止在代码中使用 pip install、subprocess、sys.executable 等安装第三方库的命令。所有依赖由系统自动处理。**
- 直接返回纯 Python 代码，不要包含 ``` 标记，不要任何解释{extra_context}"""

def build_code_generation_prompt(
    skill_name, skill_description, skill_prompt,
    user_original_input, current_action, file_paths,
    extra_context="",
    recent_history=""
) -> str:
    return CODE_GENERATION_TEMPLATE.format(
        skill_name=skill_name,
        skill_description=skill_description,
        skill_prompt=skill_prompt,
        user_original_input=user_original_input,
        current_action=current_action,
        file_paths=file_paths,
        extra_context=extra_context,
        recent_history=recent_history
    )


# ==============================
# 非代码步骤的直接回答 Prompt（新增）
# ==============================
DIRECT_ANSWER_TEMPLATE = """技能：{skill_name}
技能规则：
{skill_prompt}

历史对话：
{history}

当前任务：{action}

请直接给出专业回答，不要提问，只输出结果。"""

def build_direct_answer_prompt(
    skill_name: str,
    skill_prompt: str,
    history: str,
    action: str
) -> str:
    return DIRECT_ANSWER_TEMPLATE.format(
        skill_name=skill_name,
        skill_prompt=skill_prompt,
        history=history,
        action=action
    )


# ==============================
# 步骤评估 Prompt（两个版本）
# ==============================
# 用于需要代码的步骤（代码必须成功执行）
CODE_STEP_EVALUATION_TEMPLATE = """你是任务执行评审专家。请判断当前代码步骤是否成功完成，并给出理由。

【当前步骤】
- 步骤ID：{step_id}
- 技能：{skill_name}
- 描述：{action}

【用户原始需求】
{user_input}

【本步骤执行结果】
{tool_result}

【技能规则】
{skill_prompt}

请严格返回 JSON 格式：
{{
    "success": true/false,
    "reason": "简要理由"
}}

判断原则：
- 只要执行结果显示沙箱成功运行（无 SyntaxError、ModuleNotFoundError 等致命错误），并且输出内容基本覆盖步骤描述的任务，就应判定为成功。
- 不要因为输出缺少 JSON 或没有返回代码本身而判失败。代码步骤的输出就是 print 的内容，只要内容合理即可。
- 若输出为空或完全无关再判失败。"""

def build_code_step_evaluation_prompt(
    step_id: int,
    skill_name: str,
    action: str,
    user_input: str,
    tool_result: str,
    skill_prompt: str
) -> str:
    # 截取技能规则前 1000 字符，避免过长
    prompt_snippet = (skill_prompt or "")[:1000]
    return CODE_STEP_EVALUATION_TEMPLATE.format(
        step_id=step_id,
        skill_name=skill_name,
        action=action,
        user_input=user_input,
        tool_result=tool_result,
        skill_prompt=prompt_snippet
    )

# 用于纯文本步骤（不需要代码）
TEXT_STEP_EVALUATION_TEMPLATE = """你是任务评审专家。请判断以下文本回复是否完成了当前步骤的要求。

【当前步骤】
- 步骤ID：{step_id}
- 技能：{skill_name}
- 描述：{action}

【用户原始需求】
{user_input}

【回复内容】
{tool_result}

请返回 JSON：
{{
    "success": true/false,
    "reason": "理由"
}}
success 为 true 如果回复解决了步骤需求且内容清晰、专业。"""

def build_text_step_evaluation_prompt(
    step_id: int,
    skill_name: str,
    action: str,
    user_input: str,
    tool_result: str
) -> str:
    return TEXT_STEP_EVALUATION_TEMPLATE.format(
        step_id=step_id,
        skill_name=skill_name,
        action=action,
        user_input=user_input,
        tool_result=tool_result
    )

# ==============================
# 规划技能选择 Prompt（think_node 第一步）
# ==============================
PLANNER_SKILL_SELECTION_TEMPLATE = """你是一个智能路由器。请从以下技能中选择最适合用于**制定任务执行计划**的技能。
注意：该技能将负责把用户请求拆解为具体步骤，因此它应具备任务规划和流程组织能力。

可用技能列表：
{skills_summary}

用户请求：
"{user_input}"

请只返回所选技能的 ID（如 pipeline_master），不要返回其他内容。"""

def build_planner_skill_selection_prompt(user_input: str, skills_summary: str) -> str:
    """构造让 LLM 选择规划技能的 prompt"""
    return PLANNER_SKILL_SELECTION_TEMPLATE.format(
        skills_summary=skills_summary,
        user_input=user_input
    )


# ==============================
# 基于规划技能的步骤生成 Prompt（think_node 第二步）
# ==============================
SKILL_DRIVEN_PLAN_TEMPLATE = """你是{planner_name}，请严格按照以下技能规则生成任务执行步骤。

【技能规则】
{planner_prompt}

【用户请求】
{user_input}

【可用的执行技能（必须从以下选择）】
{available_skills}

请直接返回一个 JSON 数组，每个元素代表一个步骤，包含以下字段：
- "step_id": 整数，从1开始
- "skill_id": 该步骤使用的技能ID（必须是上述“可用执行技能”中列出的 ID，例如 data_analyzer、plot_expert、review_expert）
- "action": 步骤具体任务描述
- "requires_code": true/false，是否需要生成并执行代码

注意：
- 不要包含你自己（{planner_skill_id}）作为步骤，你只负责规划，不需要执行。
- 步骤必须按逻辑顺序排列。
- 仅返回 JSON 数组，不要任何其他内容。"""

def build_skill_driven_plan_prompt(
    planner_name: str,
    planner_prompt: str,
    user_input: str,
    planner_skill_id: str,
    available_skills: str           # 新增
) -> str:
    """使用选定的规划技能生成步骤计划"""
    return SKILL_DRIVEN_PLAN_TEMPLATE.format(
        planner_name=planner_name,
        planner_prompt=planner_prompt,
        user_input=user_input,
        planner_skill_id=planner_skill_id,
        available_skills=available_skills
    )