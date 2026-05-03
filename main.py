import typer
from rich.console import Console
from minicode.team import MiniCodeTeam

app = typer.Typer()
console = Console()


@app.command()
def run(idea: str):
    console.print("[bold green]MiniCode 正在启动 AI 开发团队...[/bold green]")

    team = MiniCodeTeam()
    result_path = team.run(idea)

    console.print(f"[bold blue]项目已生成：{result_path}[/bold blue]")


if __name__ == "__main__":
    app()