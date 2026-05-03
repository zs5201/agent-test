from setuptools import setup, find_packages

setup(
    name='agent-test',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,   # 关键：把 SKILL.md 等文件也打包进去
    install_requires=[
        'ollama>=0.5.1',
        'python-dotenv>=1.0.0',
        'pandas>=2.2.3',
        'numpy>=1.26.4',
        'scikit-learn>=1.7.1',
        'matplotlib>=3.10.3',
        'scipy>=1.15.3',
        'langgraph>=0.2.50,<2.0',
        'langchain-core>=0.1.53',
        'chromadb>=0.5.0',
        'requests>=2.31.0',
        'pillow>=10.2.0',
        'seaborn>=0.13.0',
    ],
    entry_points={
        'console_scripts': [
            'agent-test = run:main',   # 这行生成终端的 agent-test 命令
        ],
    },
    python_requires='>=3.10',
)