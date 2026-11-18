"""
Command-line interface for Open Deep Research with rich terminal styling.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .config import ResearchConfig
from .agent import DeepResearchAgent
from .report import save_reports

console = Console()

BANNER = """[bold cyan]
   ___                  ___               _           
  / _ \\___ ___ ___     / _ \\___  ___ ___ (_)__ ____   
 / // / -_) -_) _ \\   / // / _ \\(_-<-_-'/ / -_) __/   
/____/\\__/\\__/ .__/  /____/\\___/___/___//_/\\__/_/      
            /_/                                        
[/bold cyan]
[dim]⚡ Autonomous Multi-Step Research Agent • Gemini | Claude | GPT | DeepSeek | Nemotron[/dim]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Deep Dossier — Autonomous multi-step deep research agent supporting Gemini, OpenAI, Anthropic, DeepSeek, and Ollama."
    )
    parser.add_argument("topic", nargs="?", help="The topic or research question to investigate.")
    parser.add_argument("--depth", "-d", type=int, default=2, help="Research depth iterations (default: 2)")
    parser.add_argument("--breadth", "-b", type=int, default=4, help="Breadth per search step (default: 4)")
    parser.add_argument("--provider", "-p", type=str, default=None, help="LLM Provider: gemini, openai, anthropic, deepseek, nvidia, ollama, openrouter")
    parser.add_argument("--model", "-m", type=str, default=None, help="Model identifier (e.g., gemini-2.5-flash, claude-3-5-sonnet, gpt-4o, etc.)")
    parser.add_argument("--output", "-o", type=str, default="./research_outputs", help="Output directory")
    parser.add_argument("--api-key", "-k", type=str, default=None, help="API Key override")
    parser.add_argument("--base-url", type=str, default=None, help="Custom API Base URL (for Ollama, vLLM, or self-hosted endpoints)")
    parser.add_argument("--no-html", action="store_true", help="Disable HTML report generation")

    args = parser.parse_args()

    console.print(BANNER)

    topic = args.topic
    if not topic:
        topic = console.input("[bold yellow]Enter your research topic/question: [/bold yellow]").strip()

    if not topic:
        console.print("[red]Error: Research topic cannot be empty.[/red]")
        sys.exit(1)

    config = ResearchConfig(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        max_depth=args.depth,
        breadth=args.breadth,
        output_dir=Path(args.output),
        generate_html=not args.no_html,
    )

    try:
        config.validate()
    except ValueError as e:
        console.print(Panel(f"[bold red]Configuration Error:[/bold red]\n{str(e)}", border_style="red"))
        sys.exit(1)

    agent = DeepResearchAgent(config=config)

    console.print(Panel(
        f"[bold white]Topic:[/bold white] {topic}\n"
        f"[bold white]Provider:[/bold white] {agent.llm.provider.upper()} | [bold white]Model:[/bold white] {agent.llm.model}\n"
        f"[bold white]Depth:[/bold white] {config.max_depth} | [bold white]Breadth:[/bold white] {config.breadth}",
        title="[bold green]Research Mission Activated[/bold green]",
        border_style="cyan"
    ))

    with console.status("[bold green]Agent orchestrating deep research...[/bold green]", spinner="dots") as status:
        def on_progress(msg: str):
            status.update(f"[bold cyan]{msg}[/bold cyan]")
            console.print(f"  [dim]•[/dim] {msg}")

        try:
            result = agent.research(topic=topic, on_progress=on_progress)
        except Exception as e:
            console.print(f"\n[bold red]Error during research execution:[/bold red] {e}")
            sys.exit(1)

    # Save reports
    paths = save_reports(result, config.output_dir, result["slug"])

    # Output Summary Table
    table = Table(title="Generated Research Deliverables", border_style="green")
    table.add_column("Format", style="cyan", no_wrap=True)
    table.add_column("Location", style="white")

    if "markdown" in paths:
        table.add_row("Markdown (.md)", str(paths["markdown"].resolve()))
    if "html" in paths:
        table.add_row("Interactive HTML", str(paths["html"].resolve()))
    if "json" in paths:
        table.add_row("JSON Dossier", str(paths["json"].resolve()))

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold green]✨ Research Complete![/bold green] Analyzed [bold]{result['document_count']}[/bold] sources ({result['total_chars_analyzed']:,} characters).")
    console.print(f"To view HTML report in browser: [bold cyan]open {paths.get('html')}[/bold cyan]\n")


if __name__ == "__main__":
    main()
