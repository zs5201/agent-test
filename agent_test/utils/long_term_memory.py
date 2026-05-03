# utils/long_term_memory.py
"""
长期记忆模块
使用 ChromaDB 本地向量库 + Ollama nomic-embed-text 生成嵌入
实现技能规则的存储、检索、持久化
"""

import os
import sys
# 彻底关闭 Chroma 遥测 + 屏蔽所有错误日志
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"
os.environ["CHROMA_OTEL_COLLECTION_ENABLED"] = "false"
# 屏蔽 Chroma 所有日志输出
os.environ["CHROMA_LOG_LEVEL"] = "ERROR"
import logging
logging.getLogger("chromadb").setLevel(logging.CRITICAL)


import os.path
import uuid

import chromadb
import requests

from agent技术链路学习.utils.skill_manager import SKILLS

# ======================
# 全局配置
# ======================
CHROMA_DB_PATH = os.path.abspath("memory/chroma_db")
EMBEDDING_MODEL_NAME = "nomic-embed-text"
OLLAMA_EMBEDDING_API = "http://127.0.0.1:11434/api/embeddings"



# ======================
# 1. Ollama 嵌入向量生成
# ======================
def get_ollama_embedding(text: str) -> list:
    """调用本地 Ollama 获取文本向量"""
    try:
        response = requests.post(
            url=OLLAMA_EMBEDDING_API,
            json={
                "model": EMBEDDING_MODEL_NAME,
                "prompt": text
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"❌ 嵌入生成失败: {e}")
        return []

# ======================
# 2. 初始化 Chroma 客户端
# ======================
def init_long_term_memory():
    """初始化长期记忆数据库（全局只执行一次）"""
    # 创建存储目录
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    # 初始化客户端
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 获取/创建技能记忆集合
    collection = client.get_or_create_collection(
        name="agent_skill_memory",
        metadata={"description": "智能体技能规则、约束、流程长期记忆"}
    )
    print("✅ 长期记忆（ChromaDB）初始化完成")
    return client, collection


# ======================
# 3. 将所有技能存入向量库
# ======================
def build_skill_long_memory():
    """读取所有 SKILL.md 技能 → 向量化 → 存入 Chroma"""
    # 直接获取初始化后的 client 和 collection，IDE 能追踪类型
    client, skill_memory_collection = init_long_term_memory()

    # 清空旧数据（避免重复）
    try:
        client.delete_collection(name="agent_skill_memory")
        # 重新创建集合
        skill_memory_collection = client.create_collection(
            name="agent_skill_memory",
            metadata={"description": "智能体技能规则、约束、流程长期记忆"}
        )
    except Exception as e:
        print(f"⚠️ 无需清空集合，使用现有数据: {e}")

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    # 遍历所有技能
    for skill_id,  skill_info in SKILLS.items():
        content_id = f"skill_{uuid.uuid4().hex[:8]}"

        # 构造技能文档内容
        skill_content = (
            f"技能ID: {skill_id}\n"
            f"技能名称: {skill_info['name']}\n"
            f"技能描述: {skill_info['description']}\n"
            f"可用工具: {', '.join(skill_info['tools'])}\n"
            f"技能规则与执行流程:\n{skill_info['prompt']}"
        )

        # 元数据
        metadata = {
            "skill_id": skill_id,
            "skill_name": skill_info["name"],
            "category": "skill_rule"
        }

        # 生成向量
        embed = get_ollama_embedding(skill_content)
        if not embed:
            continue

        ids.append(content_id)
        documents.append(skill_content)
        embeddings.append(embed)
        metadatas.append(metadata)

    # 批量入库
    if ids:
        skill_memory_collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        print(f"✅ 已将 {len(ids)} 个技能存入长期记忆")

# ======================
# 4. 检索长期记忆（给 Agent 使用）
# ======================
def retrieve_long_memory(query: str, top_k: int = 2) -> str:
    """根据用户输入检索最相关的技能规则"""
    # 直接获取初始化后的 client 和 collection
    _, skill_memory_collection = init_long_term_memory()

    query_embed = get_ollama_embedding(query)
    if not query_embed:
        return "无可用长期记忆"

    # 向量检索
    results = skill_memory_collection.query(
        query_embeddings=[query_embed],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    if not docs:
        return "未检索到相关长期记忆"

    return "\n\n" + "="*50 + "\n\n".join(docs)