"""Rich rendering, streaming display, file save, and clipboard support."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()
err_console = Console(stderr=True)


def render_markdown(content: str, title: str = "") -> None:
    """Render content as a Rich markdown panel."""
    md = Markdown(content)
    if title:
        console.print(Panel(md, title=title, border_style="cyan", padding=(1, 2)))
    else:
        console.print(md)


def render_plain(content: str) -> None:
    """Print plain text."""
    console.print(content)


def render_json(content: str, provider: str, model: str, tokens: int) -> None:
    """Print structured JSON output."""
    import json

    data = {
        "content": content,
        "provider": provider,
        "model": model,
        "tokens_used": tokens,
    }
    console.print_json(json.dumps(data))


def stream_markdown(chunks: AsyncIterator[str]) -> str:
    """Stream chunks with live markdown rendering. Returns full content."""
    collected: list[str] = []

    async def _collect() -> None:
        with Live(Markdown(""), console=console, refresh_per_second=8) as live:
            async for chunk in chunks:
                collected.append(chunk)
                live.update(Markdown("".join(collected)))

    asyncio.run(_collect())
    return "".join(collected)


def stream_plain(chunks: AsyncIterator[str]) -> str:
    """Stream chunks as plain text. Returns full content."""
    collected: list[str] = []

    async def _collect() -> None:
        async for chunk in chunks:
            collected.append(chunk)
            console.print(chunk, end="")

    asyncio.run(_collect())
    console.print()  # newline at end
    return "".join(collected)


def save_to_file(content: str, path: str) -> Path:
    """Save content to a file and return the resolved path."""
    p = Path(path).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    err_console.print(f"[green]Saved to {p}[/green]")
    return p


def copy_to_clipboard(content: str) -> bool:
    """Copy content to clipboard. Returns True on success."""
    try:
        import pyperclip

        pyperclip.copy(content)
        err_console.print("[green]Copied to clipboard[/green]")
        return True
    except Exception:
        err_console.print("[yellow]Could not copy to clipboard (pyperclip not available)[/yellow]")
        return False


def status(msg: str):
    """Return a Rich status context manager (spinner)."""
    return err_console.status(msg, spinner="dots")


def print_error(msg: str) -> None:
    """Print an error message to stderr."""
    err_console.print(f"[bold red]Error:[/bold red] {msg}")
