# utils/tool_registry.py
"""
原子工具模块：基类定义 + 核心工具实现
遵循 LangChain Tool 规范，支持智能体自动调用
"""
from typing import Optional

import numpy as np
import pandas as pd
from langchain_core.tools import BaseTool
from matplotlib import pyplot as plt


# ------------------------------
# 1. 文件读取工具
# ------------------------------
class FileReadTool(BaseTool):
    name: str = "file_read"
    description: str = "读取本地CSV文件，返回文件内容和基本信息"

    def _run(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            info = f"文件读取成功：{file_path}\n"
            info += f"数据形状：{df.shape}\n"
            info += f"列名：{list(df.columns)}\n"
            info += f"前5行数据：\n{df.head().to_string()}"
            return info
        except Exception as e:
            return f"文件读取失败：{str(e)}"

    async def _arun(self, file_path: str) -> str:
        return self._run(file_path)

# ------------------------------
# 2. 数据分析工具（计算导数）
# ------------------------------
class DataAnalyzeTool(BaseTool):
    name: str = "data_analyze"
    description: str = "分析CSV数据，计算一阶导数、均值、方差"

    def _run(self, file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]

            dy_dx = np.gradient(y, x)
            df["dy_dx"] = dy_dx

            result = "数据分析完成\n"
            result += f"一阶导数：{list(dy_dx)}\n"
            result += f"Y轴均值：{y.mean():.2f}\n"
            result += f"Y轴方差：{y.var():.2f}"
            return result
        except Exception as e:
            return f"数据分析失败：{str(e)}"

    async def _arun(self, file_path: str) -> str:
        return self._run(file_path)

# ------------------------------
# 3. 学术图表绘制工具
# ------------------------------
class PlotTool(BaseTool):
    name: str = "plot"
    description: str = "绘制学术数据图表，保存为图片文件"

    def _run(self, file_path: str, save_path: str = "plot.png") -> str:
        try:
            plt.rcParams['font.family'] = 'Times New Roman'
            df = pd.read_csv(file_path)
            x = df.iloc[:, 0]
            y = df.iloc[:, 1]

            plt.figure(figsize=(8, 5))
            plt.plot(x, y, marker='o', color='#2E86AB', linewidth=2, markersize=6)
            plt.title('Academic Plot', fontsize=14)
            plt.xlabel('X', fontsize=12)
            plt.ylabel('Y', fontsize=12)
            plt.grid(alpha=0.3)
            plt.tight_layout()
            plt.savefig(save_path, dpi=300)
            plt.close()
            return f"绘图完成，已保存到：{save_path}"
        except Exception as e:
            return f"绘图失败：{str(e)}"

    async def _arun(self, file_path: str, save_path: str = "plot.png") -> str:
        return self._run(file_path, save_path)

# ------------------------------
# 工具注册中心（统一管理）
# ------------------------------
class ToolRegistry:
    tools = {
        "file_read": FileReadTool(),
        "data_analyze": DataAnalyzeTool(),
        "plot": PlotTool()
    }

    @staticmethod
    def get_tool(tool_name: str) -> Optional[BaseTool]:
        return ToolRegistry.tools.get(tool_name)

    @staticmethod
    def list_tools():
        return {name: tool.description for name, tool in ToolRegistry.tools.items()}