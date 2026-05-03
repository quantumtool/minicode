from minicode.agents.base import BaseAgent


class PMAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="产品经理 Agent",
            role="负责把用户的模糊想法整理成清晰、可执行的产品需求文档。"
        )

    def run(self, idea: str) -> str:
        task = f"""
用户的产品想法是：

{idea}

请输出一份 MVP 产品需求文档，包含：
1. 产品定位
2. 目标用户
3. 核心使用场景
4. MVP 功能列表
5. 暂不开发的功能
6. 验收标准
"""
        return super().run(task)