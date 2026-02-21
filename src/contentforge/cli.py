"""Root Typer application and sub-command wiring."""

from __future__ import annotations

import typer
from rich.console import Console

from contentforge import __app_name__, __version__

console = Console(stderr=True)
app = typer.Typer(
    name=__app_name__,
    help="Generate content using LLMs from your terminal.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _version_callback(value: bool) -> None:
    if value:
        from rich.text import Text

        out = Console()
        out.print(Text(f"{__app_name__} {__version__}", style="bold cyan"))
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """ContentForge - generate content using LLMs from your terminal."""


def _register_commands() -> None:
    from contentforge.commands.config_cmd import config_app
    from contentforge.commands.generate import generate_app
    from contentforge.commands.providers_cmd import providers_app
    from contentforge.commands.templates_cmd import templates_app

    app.add_typer(generate_app, name="generate", help="Generate content from templates.")
    app.add_typer(templates_app, name="templates", help="Browse available templates.")
    app.add_typer(providers_app, name="providers", help="Manage LLM providers.")
    app.add_typer(config_app, name="config", help="Manage configuration.")


_register_commands()
