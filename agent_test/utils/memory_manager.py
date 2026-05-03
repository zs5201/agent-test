# utils/memory_manager.py
"""
短期记忆（Short-term Memory）管理器
功能：存储对话历史、自动注入上下文、支持增删查
"""
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


class ShortTermMemory:
    def __init__(self):
        # 初始化 LangChain 短期记忆
        # memory_key = 上下文变量名，给LLM使用
        self.memory = InMemoryChatMessageHistory()

    def add_user_message(self, content: str):
        """
        添加用户消息到短期记忆
        """
        self.memory.add_user_message(content)

    def add_ai_message(self, content: str):
        """
        添加AI回复到短期记忆
        """
        self.memory.add_ai_message(content)

    def get_history(self):
        """
        获取完整对话历史
        """
        return self.memory.messages

    def get_history_text(self):
        """
        获取纯文本格式的对话历史（用于放入Prompt）
        """
        history = self.get_history()
        history_text = ""
        for msg in history:
            if isinstance(msg, HumanMessage):
                history_text += f"用户: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_text += f"AI: {msg.content}\n"
        return history_text

    def clear(self):
        """
        清空记忆（重置会话）
        """
        self.memory.clear()

# 创建全局记忆实例（整个智能体共享）
short_memory = ShortTermMemory()