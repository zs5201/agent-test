# utils/llm_init.py
"""
Ollama Cloud 官方 API 初始化
文档：https://docs.ollama.com/cloud
完全云端，本地无模型
"""
import os

from dotenv import load_dotenv
from ollama import Client

# 加载环境变量
load_dotenv()

def get_ollama_cloud_client():
    """
    官方标准 Cloud 客户端：
    - host=https://ollama.com
    - Authorization: Bearer API Key
    """
    client = Client(
        host="https://ollama.com",
        headers={
            "Authorization": f"Bearer {os.getenv('OLLAMA_API_KEY')}"
        }
    )
    # print(f"Bearer {os.getenv('OLLAMA_API_KEY')}")
    return client

def get_cloud_model_name():
    return os.getenv("OLLAMA_CLOUD_MODEL")