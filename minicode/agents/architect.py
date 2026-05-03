from minicode.agents.base import BaseAgent


class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="架构师 Agent",
            role="负责根据产品需求设计技术架构、目录结构和开发方案。"
        )

    def run(self, prd: str) -> str:
        task = f"""
以下是产品需求文档：

{prd}

请设计一个最小可运行的软件架构，包含：
1. 技术选型
2. 项目目录结构
3. 每个文件的作用
4. 核心模块说明
5. 开发顺序
"""
        return super().run(task)