"""Configuration management commands."""

from __future__ import annotations

from dataclasses import fields

import typer
from rich.console import Console
from rich.table import Table

from contentforge.config import Config, config_path, load_config, mask_value, set_value

config_app = typer.Typer(invoke_without_command=True)
console = Console()


@config_app.callback()
def config_show(ctx: typer.Context) -> None:
    """Show current configuration."""
    if ctx.invoked_subcommand is not None:
        return

    cfg = load_config()
    table = Table(title="Configuration", border_style="cyan")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_column("Source", style="dim")

    for f in fields(cfg):
        if f.name.startswith("_"):
            continue
        val = getattr(cfg, f.name)
        source = "env" if f.name in cfg._env_overrides else "config"
        display_val = mask_value(f.name, str(val))
        if not val and val != 0:
            display_val = "[dim]-[/dim]"
        table.add_row(f.name, display_val, source)

    console.print(table)
    console.print(f"\n[dim]Config file: {config_path()}[/dim]")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="Value to set"),
) -> None:
    """Set a configuration value."""
    try:
        set_value(key, value)
        display = mask_value(key, value)
        console.print(f"[green]Set[/green] {key} = {display}")
    except KeyError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1) from None


@config_app.command("path")
def config_path_cmd() -> None:
    """Show the config file location."""
    console.print(str(config_path()))


@config_app.command("init")
def config_init() -> None:
    """Create a default config file."""
    path = config_path()
    if path.exists():
        console.print(f"[yellow]Config already exists at {path}[/yellow]")
        return

    from contentforge.config import save_config

    save_config(Config())
    console.print(f"[green]Created config at {path}[/green]")
