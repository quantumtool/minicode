from minicode.agents.base import BaseAgent


class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="开发工程师 Agent",
            role="负责根据需求文档和架构方案生成最小可运行代码。"
        )

    def run(self, prd: str, architecture: str) -> str:
        task = f"""
以下是产品需求文档：

{prd}

以下是架构设计：

{architecture}

请生成一个最小可运行版本的代码。

要求：
1. 代码尽量简单
2. 文件结构清晰
3. 每个文件用 markdown 代码块标明文件名
4. 附带运行说明
5. 不要生成过度复杂的功能
"""
        return super().run(task)