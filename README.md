# Agent Test - 学术数据智能分析助手

基于 LLM 和 LangGraph 构建的多技能智能体系统，能够自动完成学术数据（CSV）的读取、分析、可视化、时间序列预测、结论撰写与评审。

## 🌟 功能亮点

- 🧠 **智能任务规划** - 自动分析用户需求，拆解为多步骤执行计划，动态选择最合适的专业技能
- 📊 **自动代码生成与执行** - 根据任务需求自动生成 Python 代码，在安全沙箱中执行，支持 pandas、numpy、matplotlib、sklearn 等库
- 🎨 **学术级可视化** - 自动生成符合学术规范的图表（Times New Roman 字体、300 dpi 高清输出），支持折线图、热力图、分布图等多种类型
- ✍️ **智能结论生成** - 基于分析结果自动撰写专业结论并保存为 TXT 文件
- 🔍 **自动化评审机制** - 对分析结果、图表质量和结论进行多维度评审，给出改进建议
- 🔁 **依赖自动管理** - 检测到缺失的 Python 库时，可交互询问并自动安装（默认使用清华镜像加速）
- 🛡️ **安全沙箱执行** - 所有生成的代码在隔离环境中运行，保护主环境安全
- 💾 **双层记忆系统** - 短期记忆（对话历史）+ 长期记忆（ChromaDB 向量库），保证上下文连贯性和知识复用
- 🔄 **多轮重试机制** - 每步执行失败后自动重试（最多 5 次），结合评估反馈优化代码生成

## 📋 核心技能模块

系统内置 6 大专业技能：

1. **Pipeline Master** - 任务规划与流程编排
2. **Data Analyzer** - 数据统计分析与特征工程
3. **Plot Expert** - 学术图表绘制与美化
4. **Time Series Forecaster** - 时间序列预测（支持 ROP 等钻井参数）
5. **Review Expert** - 结果评审与质量检查
6. **Conclusion Writer** - 分析结论撰写与总结

## 🚀 快速开始

### 前置要求

- Python 3.10 或更高版本
- Ollama Cloud API Key（用于调用云端大模型）

### 1. 克隆项目

```bash
git clone https://github.com/yourname/agent-test.git
cd agent-test
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或者从源码安装：

```bash
pip install -e .
```

### 3. 配置环境变量

首次运行时，程序会自动引导你配置 Ollama API Key：

```bash
python run.py
```

按提示输入你的 API Key 和模型名称（默认：`gpt-oss:120b-cloud`）。

你也可以手动创建 `.env` 文件：

```env
OLLAMA_API_KEY=your_api_key_here
OLLAMA_CLOUD_MODEL=gpt-oss:120b-cloud
```

### 4. 运行智能体

有两种启动方式：

**方式一：直接运行脚本**

```bash
python run.py
```

**方式二：使用命令行工具（推荐）**

如果你通过 `pip install -e .` 安装了项目，可以直接使用命令：

```bash
agent-test
```

然后输入你的数据分析需求，例如：

```
你的需求：帮我分析 data/F1.csv 文件，计算各特征的相关性，绘制热力图，并给出结论
```

## 📂 项目结构

```
agent_test/
├── agent_test/
│   ├── prompts/              # Prompt 模板
│   │   └── prompt_templates.py
│   ├── skills/               # 技能定义（SKILL.md）
│   │   ├── pipeline_master/
│   │   ├── data_analyzer/
│   │   ├── plot_expert/
│   │   ├── time_series_forecaster/
│   │   ├── review_expert/
│   │   └── conclusion_writer/
│   ├── utils/                # 工具模块
│   │   ├── llm_init.py       # LLM 客户端初始化
│   │   ├── skill_manager.py  # 技能管理器
│   │   ├── memory_manager.py # 短期记忆管理
│   │   ├── long_term_memory.py # 长期记忆（ChromaDB）
│   │   ├── sandbox.py        # 代码沙箱
│   │   ├── dependency_handler.py # 依赖自动安装
│   │   ├── visualizer.py     # 可视化面板
│   │   └── ...
│   └── module5_agent_loop.py # Agent 主循环（LangGraph）
├── requirements.txt          # 依赖清单
├── setup.py                  # 安装配置
├── run.py                    # 启动脚本
└── README.md
```

## 🔄 工作流程

```
用户输入 → 思考节点（选择规划技能 + 生成步骤计划）
         ↓
    行动节点（逐步骤执行：提取路径 → 生成代码 → 沙箱运行）
         ↓
    观察节点（评估步骤结果 → 成功则下一步 / 失败则重试）
         ↓
    循环直到所有步骤完成 → 输出最终结果
```

## ⚙️ 技术栈

- **LLM 框架**: LangGraph + LangChain Core
- **模型服务**: Ollama Cloud API
- **数据处理**: Pandas + NumPy
- **可视化**: Matplotlib
- **向量数据库**: ChromaDB
- **记忆管理**: InMemoryChatMessageHistory + ChromaDB
- **沙箱执行**: subprocess 隔离进程

## 📝 使用示例

### 示例 1：基础数据分析

```
你的需求：分析 data/F1.csv，计算统计指标，找出关键特征
```

### 示例 2：可视化绘图

```
你的需求：读取 data/F1.csv，绘制特征相关性热力图和分布图
```

### 示例 3：时间序列预测

```
你的需求：对 data/F1.csv 中的 ROP 数据进行时间序列预测，预测未来 100 米
```

### 示例 4：完整分析流程

```
你的需求：完整分析 data/F1.csv，包括数据探索、可视化、预测和结论
```

## 🔧 常见问题

### Q: 如何更换模型？

运行 `python run.py` 时，程序会询问是否修改模型名称，输入 `y` 即可更换。

### Q: 代码执行失败怎么办？

系统会自动检测错误并重试（最多 5 次）。如果是缺少依赖库，会提示你是否自动安装。

### Q: 生成的图表保存在哪里？

所有生成的图表保存在 `visual/` 目录下。

### Q: 如何清空记忆？

删除 `memory/chroma_db/` 目录即可清空长期记忆。

## 📄 许可证

MIT License

## 👤 作者

CSJ

---

**注意**: 本项目需要有效的 Ollama Cloud API Key 才能运行。请确保你已注册并获取了 API 密钥。
