# utils/visualizer.py
"""
可视化模块
1. LangGraph 智能体流程可视化（Mermaid/PNG）
2. 终端实时状态面板（日志/记忆/工具调用/沙箱记录）
"""
import os
from datetime import datetime

from langgraph.graph.graph import CompiledGraph

# 可视化存储目录
VISUAL_DIR = "visual"
os.makedirs(VISUAL_DIR, exist_ok=True)

class AgentVisualizer:
    """Agent 可视化与状态面板"""

    def __init__(self):
        self.logs = []
        self.tool_calls = []
        self.sandbox_records = []

    # ======================
    # 1. LangGraph 流程图可视化
    # ======================
    def save_graph_visual(self, agent: CompiledGraph) -> str:
        """生成并保存 Agent 流程图（PNG）"""
        path = os.path.join(VISUAL_DIR, f"agent_loop_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        try:
            # 生成 Mermaid 流程图图片
            image = agent.get_graph().draw_mermaid_png()
            with open(path, "wb") as f:
                f.write(image)
            self.add_log(f"✅ 流程图已保存：{path}")
            return path
        except Exception as e:
            self.add_log(f"❌ 可视化生成失败：{e}")
            return ""

    # ======================
    # 2. 日志/状态记录
    # ======================
    def add_log(self, msg: str):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def add_tool_call(self, tool_name: str, result: str):
        self.tool_calls.append({"time": datetime.now().strftime('%H:%M:%S'), "tool": tool_name, "result": result[:50]})

    def add_sandbox_run(self, code: str, status: str):
        self.sandbox_records.append({"time": datetime.now().strftime('%H:%M:%S'), "status": status, "code": code[:30]})

    # ======================
    # 3. 终端可视化面板（核心）
    # ======================
    def show_panel(self):
        """打印实时可视化状态面板（终端版）"""
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 80)
        print("📊 智能体运行可视化面板".center(80))
        print("=" * 80)

        # 运行日志
        print("\n📝 运行日志：")
        for log in self.logs[-5:]:
            print(f"  {log}")

        # 工具调用记录
        print("\n🔧 工具/MCP 调用：")
        for t in self.tool_calls[-3:]:
            print(f"  [{t['time']}] {t['tool']} | {t['result']}...")

        # 沙箱执行记录
        print("\n🛡️  沙箱执行：")
        for s in self.sandbox_records[-3:]:
            print(f"  [{s['time']}] {s['status']} | {s['code']}...")

        print("=" * 80)
        print("等待智能体执行...\n".center(80))

# 全局单例可视化
agent_visual = AgentVisualizer()