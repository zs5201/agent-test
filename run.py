import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

def ensure_config():
    """检查 .env 是否存在有效的 OLLAMA_API_KEY，若无则引导用户输入"""
    env_path = Path('.env')
    load_dotenv(env_path) if env_path.exists() else load_dotenv()  # 加载已有配置

    api_key = os.getenv('OLLAMA_API_KEY')
    model = os.getenv('OLLAMA_CLOUD_MODEL', 'llama3.1')  # 默认模型

    need_save = False
    if not api_key or api_key == 'your_api_key_here':
        print("未检测到有效的 Ollama API Key。")
        api_key = input("请输入你的 Ollama API Key: ").strip()
        if not api_key:
            print("❌ API Key 不能为空，程序退出。")
            sys.exit(1)
        need_save = True

    if need_save or not env_path.exists():
        # 写入或更新 .env
        with open(env_path, 'w') as f:
            f.write(f'OLLAMA_API_KEY={api_key}\n')
            f.write(f'OLLAMA_CLOUD_MODEL={model}\n')
        print("✅ 配置已保存到 .env")

    # 提供后续修改入口
    print(f"当前模型: {model}")
    change = input("是否需要修改模型名称？(y/n，直接回车则保持): ").strip().lower()
    if change == 'y':
        model = input("请输入新的模型名称: ").strip()
        if model:
            set_key(env_path, 'OLLAMA_CLOUD_MODEL', model)
            print(f"✅ 模型已更新为: {model}")
        else:
            print("未做修改。")

    # 重新加载环境变量以确保当前进程使用新值
    os.environ['OLLAMA_API_KEY'] = api_key
    os.environ['OLLAMA_CLOUD_MODEL'] = model

def main():
    print("🤖 学术数据智能体启动中...")
    ensure_config()

    print("输入需求即可（输入 退出/quit/exit 结束）")
    from agent_test.module5_agent_loop import run_agent

    while True:
        user_input = input("\n你的需求：")
        if user_input.strip().lower() in ("退出", "quit", "exit"):
            print("智能体已结束，再见！")
            break
        if not user_input.strip():
            continue
        try:
            run_agent(user_input)
        except Exception as e:
            print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    main()