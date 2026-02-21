"""Templates browsing commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from contentforge.templates import get_template, list_templates

templates_app = typer.Typer(invoke_without_command=True)
console = Console()


@templates_app.callback()
def templates_list(ctx: typer.Context) -> None:
    """Browse available content templates."""
    if ctx.invoked_subcommand is not None:
        return

    templates = list_templates()
    table = Table(title="Available Templates", border_style="cyan")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Category", style="dim")
    table.add_column("Description")
    table.add_column("Fields", justify="right")

    for t in templates:
        table.add_row(
            t.id,
            t.name,
            t.category,
            t.description,
            str(len(t.fields)),
        )

    console.print(table)
    console.print(
        "\n[dim]Use [cyan]contentforge templates <id>[/cyan] to see details for a template.[/dim]"
    )


@templates_app.command("show")
def show(
    template_id: str = typer.Argument(..., help="Template ID to show"),
) -> None:
    """Show detailed information about a template."""
    _show_template(template_id)


def _show_template(template_id: str) -> None:
    try:
        t = get_template(template_id)
    except KeyError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1) from None

    # Build fields table
    fields_table = Table(border_style="dim")
    fields_table.add_column("Field", style="cyan")
    fields_table.add_column("Type")
    fields_table.add_column("Required")
    fields_table.add_column("Default")
    fields_table.add_column("Options")

    for f in t.fields:
        fields_table.add_row(
            f.name,
            f.type,
            "yes" if f.required else "no",
            f.default or "-",
            ", ".join(f.options) if f.options else "-",
        )

    content = f"[bold]{t.name}[/bold] ([cyan]{t.id}[/cyan])\n"
    content += f"[dim]{t.category}[/dim]\n\n"
    content += f"{t.description}\n"

    console.print(Panel(content, border_style="cyan"))
    console.print(fields_table)

    # Show example command
    cmd_parts = [f"contentforge generate {t.id}"]
    for f in t.fields:
        if f.required:
            cmd_parts.append(f'--{f.name} "..."')
    console.print(f"\n[dim]Example:[/dim] {' '.join(cmd_parts)}")
