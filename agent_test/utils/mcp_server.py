"""
MCP 协议服务端
接收标准化请求 → 调用工具 → 返回标准化响应
"""
import json
import socket
import threading

from agent_test.utils.mcp_protocol import build_mcp_response, MCP_HOST, MCP_PORT, MCPMethods
from agent_test.utils.tool_registry import ToolRegistry


# ======================
# 处理函数：获取工具列表
# ======================
def _handle_list_tools(req_id: str, params: dict):
    tools = ToolRegistry.list_tools()
    return build_mcp_response(req_id=req_id, result=tools)

# ======================
# 处理函数：调用单个工具
# ======================
def _handle_call_tool(req_id: str, params: dict):
    tool_name = params.get("name")
    tool_args = params.get("args", {})
    tool = ToolRegistry.get_tool(tool_name)

    if not tool:
        return build_mcp_response(
            req_id=req_id,
            error={"code": -1, "message": f"工具 {tool_name} 不存在"}
        )

    result = tool.invoke(tool_args)
    return build_mcp_response(req_id=req_id, result={
        "tool": tool_name,
        "result": result,
        "status": "success"
    })


class MCPServer:
    def __init__(self):
        self.host = MCP_HOST
        self.port = MCP_PORT
        self.server_socket = None
        self.is_running = False

        # 核心：方法路由表（字典映射）
        self.handler_map = {
            MCPMethods.LIST_TOOLS: _handle_list_tools,
            MCPMethods.CALL_TOOL: _handle_call_tool
        }

    # ======================
    # 处理 MCP 请求
    # ======================
    def handle_request(self, data: str) -> str:
        try:
            request = json.loads(data)
            req_id = request.get("id", "")
            method = request.get("method", "")
            params = request.get("params", {})

            if method not in self.handler_map:
                resp = build_mcp_response(
                    req_id=req_id,
                    error={"code": -2, "message": f"未知方法：{method}"}
                )
                return json.dumps(resp)

            handler_func = self.handler_map[method]
            resp = handler_func(req_id=req_id, params=params)
            return json.dumps(resp)

        except Exception as e:
            resp = build_mcp_response(
                req_id="error",
                error={"code": -3, "message": f"处理请求失败：{str(e)}"}
            )
            return json.dumps(resp)

    # ======================
    # 启动服务端
    # ======================
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True
        print(f"✅ MCP 服务端启动: {self.host}:{self.port}")

        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                data = conn.recv(4096).decode("utf-8")
                if data:
                    response = self.handle_request(data)
                    conn.sendall(response.encode("utf-8"))
                conn.close()
            except Exception:
                break

    def start_in_thread(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def stop(self):
        self.is_running = False
        self.server_socket.close()

# 全局单例服务
mcp_server = MCPServer()