# utils/dependency_handler.py
"""
依赖自动检测与安装工具
当沙箱执行代码因缺少第三方库而失败时，自动提取缺失模块并询问用户安装。
"""
import re
import site
import subprocess
import sys


def extract_missing_module(err_detail: str) -> list:
    """
    从错误信息中提取 ModuleNotFoundError 的缺失模块名。
    返回去重后的模块名列表。
    """
    missing = re.findall(r"No module named '(\w+)'", err_detail)
    return list(set(missing))

def try_install_modules(missing_modules: list, auto_confirm: bool = False, use_mirror: bool = True) -> bool:
    """
    询问用户是否安装缺失模块，若同意则 pip install，默认使用清华镜像源加速。
    返回 True 表示所有模块安装成功，False 表示用户拒绝或安装失败。

    :param auto_confirm: 若为 True，则无需用户输入直接安装（谨慎使用）。
    """
    if not missing_modules:
        return False

    # 获取安装环境信息
    python_path = sys.executable
    # 尝试获取 pip 安装目标路径（使用 sysconfig 或 site）
    try:
        import sysconfig
        target_dir = sysconfig.get_path('purelib')
    except Exception:
        target_dir = site.getsitepackages()[0] if site.getsitepackages() else '未知'

    print(f"\n⚠️ 检测到缺失模块: {', '.join(missing_modules)}")
    print(f"📌 将安装到 Python 环境: {python_path}")
    print(f"📁 pip 安装目标路径: {target_dir}")

    print(f"\n⚠️ 检测到缺失模块: {', '.join(missing_modules)}")
    if auto_confirm:
        confirm = 'y'
    else:
        confirm = input(f"是否自动安装？(y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ 用户拒绝安装，跳过此步骤。")
        return False

    for mod in missing_modules:
        print(f"📦 正在安装 {mod} ...")
        # 构建安装命令，使用国内镜像
        cmd = [sys.executable, "-m", "pip", "install", mod]
        if use_mirror:
            cmd += ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
        try:
            subprocess.check_call(cmd)
            print(f"✅ {mod} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {mod} 安装失败: {e}")
            return False
    return True