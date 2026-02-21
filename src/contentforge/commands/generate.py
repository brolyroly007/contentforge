"""Generate subcommands - 8 content types."""

from __future__ import annotations

import asyncio

import typer

from contentforge import output
from contentforge.config import load_config
from contentforge.providers import get_provider
from contentforge.templates import get_template

generate_app = typer.Typer(no_args_is_help=True)

# ── Shared options ──────────────────────────────────────────────

_provider_opt = typer.Option(None, "--provider", "-p", help="LLM provider (openai/gemini/ollama)")
_model_opt = typer.Option(None, "--model", "-m", help="Model override")
_output_opt = typer.Option(None, "--output", "-o", help="Save to file")
_format_opt = typer.Option(None, "--format", "-f", help="Output format (markdown/plain/json)")
_copy_opt = typer.Option(False, "--copy", help="Copy result to clipboard")
_stream_opt = typer.Option(None, "--stream/--no-stream", help="Enable/disable streaming")
_temp_opt = typer.Option(None, "--temperature", help="Sampling temperature (0.0-2.0)")
_max_tokens_opt = typer.Option(None, "--max-tokens", help="Max output tokens")


def _run_generation(
    template_id: str,
    variables: dict[str, str],
    provider: str | None,
    model: str | None,
    output_file: str | None,
    fmt: str | None,
    copy: bool,
    do_stream: bool | None,
    temperature: float | None,
    max_tokens: int | None,
) -> None:
    """Core generation logic shared by all subcommands."""
    cfg = load_config()
    fmt = fmt or cfg.default_format
    do_stream = do_stream if do_stream is not None else cfg.stream
    temperature = temperature if temperature is not None else cfg.default_temperature
    max_tokens = max_tokens if max_tokens is not None else cfg.default_max_tokens

    try:
        tpl = get_template(template_id)
    except KeyError as e:
        output.print_error(str(e))
        raise typer.Exit(1) from None

    # Fill defaults for missing optional fields
    for field in tpl.fields:
        if field.name not in variables or not variables[field.name]:
            if field.default:
                variables[field.name] = field.default
            elif not field.required:
                variables[field.name] = ""

    # Special handling for blog keywords line
    if template_id == "blog":
        kw = variables.get("keywords", "")
        variables["keywords_line"] = f"Include these SEO keywords naturally: {kw}" if kw else ""
    if "keywords_line" not in variables:
        variables["keywords_line"] = ""

    # Build prompt
    try:
        user_prompt = tpl.user_prompt_template.format(**variables)
    except KeyError as e:
        output.print_error(f"Missing required field: {e}")
        raise typer.Exit(1) from None

    try:
        prov = get_provider(provider, model)
    except ValueError as e:
        output.print_error(str(e))
        raise typer.Exit(1) from None

    output.err_console.print(
        f"[dim]Using {prov.name}/{prov.model} • template: {template_id}[/dim]"
    )

    content = ""
    tokens = 0

    if do_stream and fmt != "json":
        # Stream iterator must be created and consumed in the same event loop,
        # so we pass the provider directly and let output handle asyncio.run().
        chunks = prov.stream(user_prompt, tpl.system_prompt, temperature, max_tokens)
        content = (
            output.run_stream_plain(chunks)
            if fmt == "plain"
            else output.run_stream_markdown(chunks)
        )
    else:
        with output.status("Generating..."):
            result = asyncio.run(
                prov.generate(user_prompt, tpl.system_prompt, temperature, max_tokens)
            )
        content = result.content
        tokens = result.tokens_used

        if fmt == "json":
            output.render_json(content, prov.name, prov.model, tokens)
        elif fmt == "plain":
            output.render_plain(content)
        else:
            output.render_markdown(content, title=tpl.name)

    if output_file:
        output.save_to_file(content, output_file)
    if copy:
        output.copy_to_clipboard(content)


# ── Subcommands ─────────────────────────────────────────────────


@generate_app.command()
def blog(
    topic: str = typer.Option(..., "--topic", help="Blog topic"),
    tone: str = typer.Option("professional", "--tone", help="Tone: professional/casual/academic/conversational"),
    word_count: int = typer.Option(800, "--word-count", help="Target word count"),
    keywords: str | None = typer.Option(None, "--keywords", help="SEO keywords (comma-separated)"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate a blog post."""
    _run_generation(
        "blog",
        {"topic": topic, "tone": tone, "word_count": str(word_count), "keywords": keywords or ""},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def social(
    topic: str = typer.Option(..., "--topic", help="Post topic"),
    platform: str = typer.Option("linkedin", "--platform", help="Platform: linkedin/instagram/twitter/facebook"),
    goal: str = typer.Option("engagement", "--goal", help="Goal: engagement/awareness/traffic/conversion"),
    hashtags: str = typer.Option("yes", "--hashtags", help="Include hashtags: yes/no"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate a social media post."""
    _run_generation(
        "social",
        {"platform": platform, "topic": topic, "goal": goal, "include_hashtags": hashtags},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def email(
    subject: str = typer.Option(..., "--subject", help="Email subject/context"),
    type: str = typer.Option("marketing", "--type", help="Type: marketing/cold-outreach/newsletter/follow-up/announcement"),
    recipient: str = typer.Option("customers", "--recipient", help="Target recipient"),
    cta: str | None = typer.Option(None, "--cta", help="Call to action"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate an email with subject line."""
    _run_generation(
        "email",
        {"type": type, "subject": subject, "recipient": recipient, "cta": cta or ""},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command("tweet-thread")
def tweet_thread(
    topic: str = typer.Option(..., "--topic", help="Thread topic"),
    count: int = typer.Option(8, "--count", help="Number of tweets"),
    style: str = typer.Option("educational", "--style", help="Style: educational/storytelling/listicle/controversial-take"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate a Twitter/X thread."""
    _run_generation(
        "tweet-thread",
        {"topic": topic, "count": str(count), "style": style},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def ad(
    product: str = typer.Option(..., "--product", help="Product or service"),
    audience: str = typer.Option(..., "--audience", help="Target audience"),
    platform: str = typer.Option("google-ads", "--platform", help="Platform: google-ads/facebook-ads/instagram-ads/linkedin-ads"),
    usp: str | None = typer.Option(None, "--usp", help="Unique selling point"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate ad copy for a platform."""
    _run_generation(
        "ad",
        {"platform": platform, "product": product, "audience": audience, "usp": usp or ""},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def seo(
    keyword: str = typer.Option(..., "--keyword", help="Primary keyword"),
    page_type: str = typer.Option("blog-post", "--page-type", help="Page type: blog-post/landing-page/product-page/homepage"),
    secondary_keywords: str | None = typer.Option(None, "--secondary-keywords", help="Secondary keywords (comma-separated)"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate SEO meta tags."""
    _run_generation(
        "seo",
        {"keyword": keyword, "page_type": page_type, "secondary_keywords": secondary_keywords or ""},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def product(
    name: str = typer.Option(..., "--name", help="Product name"),
    features: str = typer.Option(..., "--features", help="Key features (comma-separated)"),
    audience: str | None = typer.Option(None, "--audience", help="Target audience"),
    tone: str = typer.Option("friendly", "--tone", help="Tone: premium/friendly/technical/minimalist"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate a product description."""
    _run_generation(
        "product",
        {"name": name, "features": features, "audience": audience or "", "tone": tone},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )


@generate_app.command()
def youtube(
    title: str = typer.Option(..., "--title", help="Video title"),
    summary: str = typer.Option(..., "--summary", help="Video summary"),
    keywords: str | None = typer.Option(None, "--keywords", help="Keywords (comma-separated)"),
    timestamps: str = typer.Option("yes", "--timestamps", help="Include timestamps: yes/no"),
    provider: str | None = _provider_opt,
    model: str | None = _model_opt,
    output_file: str | None = _output_opt,
    fmt: str | None = _format_opt,
    copy: bool = _copy_opt,
    stream: bool | None = _stream_opt,
    temperature: float | None = _temp_opt,
    max_tokens: int | None = _max_tokens_opt,
) -> None:
    """Generate a YouTube video description."""
    _run_generation(
        "youtube",
        {"title": title, "summary": summary, "keywords": keywords or "", "timestamps": timestamps},
        provider, model, output_file, fmt, copy, stream, temperature, max_tokens,
    )
