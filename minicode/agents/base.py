from minicode.llm import call_llm


class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def build_prompt(self, task: str) -> str:
        return f"""
你是 {self.name}。
你的角色是：{self.role}

请完成以下任务：

{task}
"""

    def run(self, task: str) -> str:
        prompt = self.build_prompt(task)
        return call_llm(prompt)