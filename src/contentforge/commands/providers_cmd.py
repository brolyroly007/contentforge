"""Provider management commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from contentforge.config import load_config
from contentforge.providers import list_providers

providers_app = typer.Typer(invoke_without_command=True)
console = Console()


@providers_app.callback()
def providers_list(ctx: typer.Context) -> None:
    """List available LLM providers and their status."""
    if ctx.invoked_subcommand is not None:
        return

    cfg = load_config()
    providers = list_providers()

    table = Table(title="LLM Providers", border_style="cyan")
    table.add_column("Provider", style="bold")
    table.add_column("Status")
    table.add_column("Default Model")
    table.add_column("Models")
    table.add_column("Default", justify="center")

    for p in providers:
        status = "[green]available[/green]" if p["available"] else "[red]not configured[/red]"
        is_default = "[cyan]*[/cyan]" if p["name"] == cfg.default_provider else ""
        table.add_row(
            p["name"],
            status,
            p.get("default_model", p["models"][0]),
            ", ".join(p["models"][:3]) + ("..." if len(p["models"]) > 3 else ""),
            is_default,
        )

    console.print(table)
    console.print(f"\n[dim]Default provider: [cyan]{cfg.default_provider}[/cyan][/dim]")


@providers_app.command("check")
def check() -> None:
    """Test connectivity to all providers."""
    providers = list_providers()

    for p in providers:
        name = p["name"]
        if p["available"]:
            console.print(f"  [green]✓[/green] {name}: connected")
        else:
            console.print(f"  [red]✗[/red] {name}: not available")
