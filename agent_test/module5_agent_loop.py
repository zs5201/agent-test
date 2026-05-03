# module5_agent_loop.py
"""
模块5：Agent 主循环（LangGraph ReAct）
流程：think → act → observe → end
"""
import json
import re
from typing import TypedDict, Dict

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END
from langgraph.graph import StateGraph

from agent_test.prompts.prompt_templates import build_planner_skill_selection_prompt, \
    build_skill_driven_plan_prompt, build_file_path_extraction_prompt, build_code_generation_prompt, \
    build_direct_answer_prompt, build_code_step_evaluation_prompt, build_text_step_evaluation_prompt
from agent_test.utils.dependency_handler import extract_missing_module, try_install_modules
from agent_test.utils.llm_init import get_ollama_cloud_client, get_cloud_model_name
from agent_test.utils.memory_manager import short_memory
from agent_test.utils.sandbox import safe_sandbox
from agent_test.utils.skill_manager import get_available_skills_summary, get_skill, SKILLS
from agent_test.utils.visualizer import agent_visual


# ======================
# 1. 定义 Agent 状态 State（核心）
# ======================
class AgentState(TypedDict):
    input: str
    current_skill: Dict
    memory: list
    tool_result: str
    thought: str
    is_done: bool
    round_count: int
    task_plan: list
    current_step_index: int
    step_retry_count: int        # 新增：当前步骤重试次数
    last_feedback: str   # 上一轮观察节点给出的失败原因

# ======================
# 2. 节点1：思考（选择技能 + 决策）
# ======================
def think_node(state: AgentState):
    user_input = state["input"]
    round_count = state["round_count"]
    print(f"\n🤔 【思考节点｜第 {round_count} 轮】")

    client = get_ollama_cloud_client()
    model = get_cloud_model_name()
    skill_summary = get_available_skills_summary()

    # ===== 第一步：让 LLM 自主选择用于规划的 Skill =====
    selection_prompt = build_planner_skill_selection_prompt(user_input, skill_summary)
    resp = client.chat(
        model=model,
        messages=[{"role": "user", "content": selection_prompt}],
        stream=False
    )
    planner_skill_id = resp["message"]["content"].strip()
    print(f"🧠 LLM 选择了规划技能：{planner_skill_id}")

    planner_skill = get_skill(planner_skill_id)
    if not planner_skill:
        planner_skill_id = "pipeline_master"
        planner_skill = get_skill(planner_skill_id)
    print(f"📌 实际使用的规划技能：{planner_skill['name']}")

    # ===== 第二步：用选中的规划技能生成步骤计划 =====
    # 获取除规划技能外的可执行技能摘要（避免 LLM 再把规划技能放到步骤里）
    execution_skills_summary = "\n".join(
        f"- **{sid}**: {skill['name']} —— {skill['description']}"
        for sid, skill in SKILLS.items()
        if sid != planner_skill_id
    )

    plan_prompt = build_skill_driven_plan_prompt(
        planner_name=planner_skill["name"],
        planner_prompt=planner_skill["prompt"],
        user_input=user_input,
        planner_skill_id=planner_skill_id,
        available_skills=execution_skills_summary  # 传入可用执行技能列表
    )

    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": plan_prompt}],
        stream=False
    )
    llm_output = response["message"]["content"]

    # 解析 JSON
    try:
        json_match = re.search(r'\[.*\]', llm_output, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group(0))
        else:
            raise ValueError("未找到JSON数组")
    except Exception as e:
        print(f"⚠️ 计划生成失败: {e}，使用默认计划")
        plan = [{"step_id": 1, "skill_id": "data_analyzer", "action": user_input, "requires_code": True}]

    print(f"📋 任务计划共 {len(plan)} 步：")
    for step in plan:
        print(f"  Step {step['step_id']}: [{step['skill_id']}] {step['action']} "
              f"(需要代码: {step.get('requires_code', False)})")

    return {
        "task_plan": plan,
        "current_step_index": 0,
        "step_retry_count": 0,
        "round_count": round_count + 1,
        "thought": f"使用 {planner_skill['name']} 生成{len(plan)}步计划"
    }

# ======================
# 3. 节点2：行动（调用 Tool）
# ======================
def act_node(state: AgentState):
    print("\n⚙️ 【行动节点：按步执行】")
    plan = state["task_plan"]
    index = state["current_step_index"]

    if index >= len(plan):
        print("✅ 所有步骤已执行完毕")
        return {"tool_result": "所有步骤已完成"}

    step = plan[index]
    skill_id = step["skill_id"]
    action = step["action"]
    requires_code = step.get("requires_code", False)

    skill = get_skill(skill_id)
    print(f"▶️ 执行 Step {step['step_id']}: {action} (技能: {skill['name']})")

    client = get_ollama_cloud_client()
    model = get_cloud_model_name()

    # ---------- 需要代码的步骤 ----------
    if requires_code:
        # 1) 提取文件路径
        path_prompt = build_file_path_extraction_prompt(state['input'])
        resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": path_prompt}],
            stream=False
        )
        file_paths = resp["message"]["content"].strip()
        print(f"📂 当前步骤文件路径：{file_paths}")

        # 如果当前步骤有重试（step_retry_count > 0），把上次失败原因加到 prompt 中
        retry_info = ""
        if state.get("step_retry_count", 0) > 0 and state.get("last_feedback"):
            retry_info = (
                "\n\n【重要】上一次尝试失败，评估给出的具体原因如下：\n"
                f"{state['last_feedback']}\n"
                "请修正上述问题，重新生成代码。"
            )

        # 2) 生成代码
        extra = retry_info if retry_info else ""
        recent_history = short_memory.get_history_text()  # 包含之前所有步骤的真实输出
        code_prompt = build_code_generation_prompt(
            skill_name=skill["name"],
            skill_description=skill["description"],
            skill_prompt=skill["prompt"],
            user_original_input=state["input"],
            current_action=action,
            file_paths=file_paths,
            extra_context=extra,
            recent_history=recent_history
        )

        code_resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": code_prompt}],
            stream=False
        )
        generated_code = code_resp["message"]["content"].replace("```python", "").replace("```", "").strip()
        print("📝 生成代码：\n" + generated_code + "...")

        # 3) 沙箱执行
        sand_result = None
        code_to_run = generated_code
        while True:
            print("🛡️ 沙箱执行中...")
            sand_result = safe_sandbox.run(code_to_run, timeout=6000)
            status = sand_result["status"]
            if status == "success":
                break

            err_detail = sand_result.get('stderr') or sand_result.get('error', '')
            # 检查是否是缺失模块导致
            if "ModuleNotFoundError" in err_detail:
                missing_mods = extract_missing_module(err_detail)
                if missing_mods:
                    installed = try_install_modules(missing_mods)
                    if installed:
                        print("🔁 模块安装完成，重新执行原代码...")
                        agent_visual.add_log("模块缺失，已自动安装后重试")
                        continue
                    else:
                        print("❌ 无法安装缺失模块，步骤失败")
                        break
                else:
                    break
            else:
                break

        agent_visual.add_sandbox_run(code_to_run, sand_result["status"])
        status = sand_result["status"]
        if status == "success":
            step_result = f"Step {step['step_id']} 执行成功\n输出：\n{sand_result.get('stdout', '')}"
        else:
            err_detail = sand_result.get('stderr') or sand_result.get('error', '')
            step_result = f"Step {step['step_id']} 执行失败\n错误详情：\n{err_detail}"
            print(f"❌ 沙箱错误详情：{err_detail}")

    # ---------- 不需要代码的步骤（纯文本） ----------
    else:
        history = short_memory.get_history_text()
        answer_prompt = build_direct_answer_prompt(
            skill_name=skill["name"],
            skill_prompt=skill["prompt"],
            history=history,
            action=action
        )
        answer_resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": answer_prompt}],
            stream=False
        )
        step_result = answer_resp["message"]["content"]

    print(f"✅ Step {step['step_id']} 结果：\n{step_result}")
    agent_visual.add_log(f"Step {step['step_id']} 完成")

    # 注意：只返回 tool_result，不修改 current_step_index
    return {"tool_result": step_result}

# ======================
# 4. 节点3：观察（整理结果 + 判断任务是否完成）
# ======================
def observe_node(state: AgentState):
    print("\n👁️ 【观察节点｜评估当前步骤】")
    plan = state["task_plan"]
    index = state.get("current_step_index", 0)
    total_steps = len(plan)

    if index >= total_steps:
        print("🎉 所有步骤执行完毕，任务完成")
        short_memory.add_user_message(state["input"])
        short_memory.add_ai_message("所有步骤已完成，结果如上。")
        return {"is_done": True}

    current_step = plan[index]
    step_id = current_step["step_id"]
    action = current_step["action"]
    skill_id = current_step["skill_id"]
    skill = get_skill(skill_id)
    requires_code = current_step.get("requires_code", False)
    tool_result = state["tool_result"]

    client = get_ollama_cloud_client()
    model = get_cloud_model_name()

    # 根据步骤类型选择评估 Prompt
    if requires_code:
        eval_prompt = build_code_step_evaluation_prompt(
            step_id=step_id,
            skill_name=skill["name"],
            action=action,
            user_input=state["input"],
            tool_result=tool_result,
            skill_prompt=skill.get("prompt", "")
        )
    else:
        eval_prompt = build_text_step_evaluation_prompt(
            step_id=step_id,
            skill_name=skill["name"],
            action=action,
            user_input=state["input"],
            tool_result=tool_result
        )

    resp = client.chat(
        model=model,
        messages=[{"role": "user", "content": eval_prompt}],
        stream=False
    )
    eval_output = resp["message"]["content"]
    print(f"🔍 LLM 评估原始输出：{eval_output}")

    # 解析评估结果
    import json, re
    success = False
    reason = ""
    try:
        json_match = re.search(r'\{.*\}', eval_output, re.DOTALL)
        if json_match:
            eval_json = json.loads(json_match.group(0))
            success = eval_json.get("success", False)
            reason = eval_json.get("reason", "")
    except Exception as e:
        print(f"⚠️ 评估解析失败: {e}，默认认为成功")
        success = True
        reason = "评估解析异常，默认通过"

    print(f"✅ 评估结果：{'成功' if success else '失败'} - {reason}")

    MAX_RETRIES = 5
    if success:
        print("✅ 当前步骤完成，进入下一步")
        short_memory.add_user_message(f"步骤{step_id}完成: {action}")
        short_memory.add_ai_message(tool_result)
        next_index = index + 1
        is_done = next_index >= total_steps
        return {
            "is_done": is_done,
            "current_step_index": next_index,
            "step_retry_count": 0,
            "last_feedback": ""
        }
    else:
        retries = state.get("step_retry_count", 0) + 1
        if retries <= MAX_RETRIES:
            print(f"⚠️ 步骤失败，重试第 {retries} 次")
            return {
                "is_done": False,
                "current_step_index": index,
                "step_retry_count": retries,
                "last_feedback": reason  # 把评估失败的具体原因传下去
            }
        else:
            print(f"❌ 重试已达上限，强制进入下一步")
            short_memory.add_user_message(f"步骤{step_id}失败（已重试{MAX_RETRIES}次）")
            next_index = index + 1
            is_done = next_index >= total_steps
            return {
                "is_done": is_done,
                "current_step_index": next_index,
                "step_retry_count": 0,
                "last_feedback": ""
            }

# ======================
# 5. 结束节点
# ======================
def should_end(state: AgentState):
    # 如果观察节点判定任务完成，就结束
    if state["is_done"]:
        return END
    # 否则回到行动节点，继续执行下一步或重试当前步
    return "act"

# ======================
# 6. 构建 LangGraph 流程
# ======================
def build_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("think", think_node)
    workflow.add_node("act", act_node)
    workflow.add_node("observe", observe_node)

    workflow.set_entry_point("think")
    workflow.add_edge("think", "act")
    workflow.add_edge("act", "observe")

    # 条件边：若未完成，回到 act 继续执行下一步（或重试当前步）
    workflow.add_conditional_edges(
        "observe",
        should_end
    )

    return workflow.compile()

# ======================
# 运行智能体
# ======================
def run_agent(user_input: str):
    print("=" * 60)
    print("🚀 智能体启动")
    print("流程：思考 → 行动 → 观察 → 结束")
    print("=" * 60)

    agent = build_agent()

    initial_state = {
        "input": user_input,
        "current_skill": {},
        "memory": [],
        "tool_result": "",
        "thought": "",
        "is_done": False,
        "round_count": 1
    }

    config = RunnableConfig(recursion_limit=100)
    agent.invoke(initial_state, config=config)
    print("\n🏁 任务完成！")

# if __name__ == "__main__":
#     # 测试：自动执行完整流程
#     run_agent("帮我分析数据")