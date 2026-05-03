# utils/mcp_protocol.py
"""
MCP 协议标准化定义
基于 JSON-RPC 2.0，实现工具调用标准化
"""
import uuid
from typing import Dict, Any

# ======================
# MCP 协议核心常量
# ======================
JSONRPC_VERSION = "2.0"
MCP_HOST = "127.0.0.1"
MCP_PORT = 65432

# ======================
# 1. 构建标准 MCP 请求
# ======================
def build_mcp_request(method: str, params: Dict[str, Any] = None) -> Dict:
    """
    构建标准 MCP 请求
    :param method: 方法名 tools/list / tools/call
    :param params: 参数
    """
    return {
        "jsonrpc": JSONRPC_VERSION,
        "id": f"mcp_{uuid.uuid4().hex[:8]}",
        "method": method,
        "params": params or {}
    }

# ======================
# 2. 构建标准 MCP 响应
# ======================
def build_mcp_response(req_id: str, result: Any = None, error: Dict = None) -> Dict:
    """构建标准 MCP 响应"""
    response = {
        "jsonrpc": JSONRPC_VERSION,
        "id": req_id
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result
    return response

# ======================
# 3. MCP 方法定义
# ======================
class MCPMethods:
    LIST_TOOLS = "tools/list"       # 获取所有工具
    CALL_TOOL = "tools/call"       # 调用单个工具