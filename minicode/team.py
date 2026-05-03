from rich.console import Console
from minicode.agents.pm import PMAgent
from minicode.agents.architect import ArchitectAgent
from minicode.agents.developer import DeveloperAgent
from minicode.workspace import save_project_result

console = Console()


class MiniCodeTeam:
    def __init__(self):
        self.pm = PMAgent()
        self.architect = ArchitectAgent()
        self.developer = DeveloperAgent()

    def run(self, idea: str) -> str:
        console.print("[yellow]PM Agent 正在生成需求文档...[/yellow]")
        prd = self.pm.run(idea)

        console.print("[yellow]Architect Agent 正在设计架构...[/yellow]")
        architecture = self.architect.run(prd)

        console.print("[yellow]Developer Agent 正在生成代码...[/yellow]")
        code = self.developer.run(prd, architecture)

        result_path = save_project_result(
            idea=idea,
            prd=prd,
            architecture=architecture,
            code=code,
        )

        return result_path