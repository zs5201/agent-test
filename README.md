# Drill Agent - 智能钻井数据分析助手

基于 LLM 的多技能 Agent，能自动完成钻井数据（CSV）的读取、分析、可视化、结论撰写与评审。

## 功能亮点
- 🧠 自动规划任务步骤，选择匹配的专业技能（数据分析、绘图、预测、评审等）
- 📊 自动编写并运行 Python 代码，生成学术级图表（Times New Roman, 300 dpi）
- ✍️ 自动生成分析结论并保存为 TXT 文件
- 🔍 自动评审分析结果、图表和结论，给出改进建议
- 🔁 遇到依赖缺失可交互询问并自动安装（默认使用清华镜像）
- 🧪 代码在安全沙箱中执行，不影响主环境
- 🗂️ 支持短期 + 长期记忆（ChromaDB），上下文连贯

## 安装要求
- Python 3.10 或以上
- 依赖库（见 `requirements.txt`），安装时会自动处理
- Ollama Cloud API Key（用于调用远端大模型）

## 快速开始

### 1. 获取代码
```bash
git clone https://github.com/yourname/drill-agent.git
cd drill-agent