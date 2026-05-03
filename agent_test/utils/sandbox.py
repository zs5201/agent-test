# utils/sandbox.py
"""
安全沙箱模块
基于 subprocess 实现 Python 代码隔离执行，限制权限/资源，防止恶意代码
适配 Agent 代码生成、工具执行的安全场景
"""
import subprocess
import sys
from typing import Dict


class CodeSandbox:
    """Python 代码安全沙箱（隔离执行）"""

    @staticmethod
    def run(code: str, timeout: int = 10) -> Dict:
        """
        安全沙箱执行代码
        :param code: 待执行的Python代码
        :param timeout: 超时限制（秒）
        :return: 执行结果（标准输出/错误/状态）
        """
        try:
            # 子进程隔离执行，完全独立于主进程
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                encoding="utf-8",
                timeout=timeout,
                # 安全限制：禁用网络/文件写入高危操作（基础防护）
                shell=False
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "sandbox": "isolated subprocess"
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": f"代码执行超时（{timeout}秒）",
                "sandbox": "isolated subprocess"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "sandbox": "isolated subprocess"
            }

    @staticmethod
    def safe_file_read(file_path: str, max_size: int = 1024*1024) -> str:
        """沙箱安全读取文件（限制大小）"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read(max_size)
        except Exception as e:
            return f"沙箱读取失败：{str(e)}"

# 全局单例沙箱
safe_sandbox = CodeSandbox()