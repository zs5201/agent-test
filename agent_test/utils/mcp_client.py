# utils/mcp_client.py
"""
MCP 协议客户端
Agent 通过该客户端标准化调用工具
"""
import json
import socket

from agent_test.utils.mcp_protocol import MCP_HOST, MCP_PORT, build_mcp_request, MCPMethods


class MCPClient:
    def __init__(self):
        self.host = MCP_HOST
        self.port = MCP_PORT

    # ======================
    # 发送 MCP 请求
    # ======================
    def send_request(self, method: str, params: dict = None):
        try:
            request = build_mcp_request(method, params)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((self.host, self.port))
                s.sendall(json.dumps(request).encode("utf-8"))

                # ✅ 循环接收直到连接关闭
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                response = json.loads(data.decode("utf-8"))
            return response
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -999, "message": f"客户端请求失败：{str(e)}"}
            }

    # ======================
    # 标准化工具调用
    # ======================
    def call_tool(self, tool_name: str, args: dict = None):
        return self.send_request(
            method=MCPMethods.CALL_TOOL,
            params={"name": tool_name, "args": args or {}}
        )

    # ======================
    # 获取工具列表
    # ======================
    def list_tools(self):
        return self.send_request(method=MCPMethods.LIST_TOOLS)

# 全局单例客户端
mcp_client = MCPClient()