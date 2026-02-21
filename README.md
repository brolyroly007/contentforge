# ContentForge

**CLI tool for generating content using LLMs from your terminal.**

[![PyPI](https://img.shields.io/pypi/v/contentforge)](https://pypi.org/project/contentforge/)
[![Python](https://img.shields.io/pypi/pyversions/contentforge)](https://pypi.org/project/contentforge/)
[![CI](https://github.com/brolyroly007/contentforge/actions/workflows/ci.yml/badge.svg)](https://github.com/brolyroly007/contentforge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate blog posts, social media content, emails, ad copy, and more — powered by OpenAI, Gemini, or local Ollama models.

## Installation

```bash
pip install contentforge
```

## Quick Start

```bash
# Configure your API key
contentforge config set openai_api_key sk-your-key-here

# Generate a blog post
contentforge generate blog --topic "AI trends in 2026" --tone professional

# Generate a LinkedIn post
contentforge generate social --platform linkedin --topic "Remote work" --goal engagement

# Generate with streaming (default)
contentforge generate email --subject "Product launch" --type marketing

# Save to file
contentforge generate blog --topic "Python tips" -o blog.md

# Copy to clipboard
contentforge generate social --topic "Coding" --copy
```

## Supported Content Types

| Command | Description |
|---------|-------------|
| `generate blog` | Blog posts with SEO optimization |
| `generate social` | Platform-optimized social media posts |
| `generate email` | Professional emails with subject lines |
| `generate tweet-thread` | Twitter/X threads |
| `generate ad` | Ad copy for Google, Facebook, Instagram, LinkedIn |
| `generate seo` | SEO meta tags and keywords |
| `generate product` | Product descriptions |
| `generate youtube` | YouTube video descriptions |

## Providers

ContentForge supports three LLM providers:

| Provider | Models | Setup |
|----------|--------|-------|
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4-turbo | `contentforge config set openai_api_key YOUR_KEY` |
| **Gemini** | gemini-2.0-flash, gemini-1.5-pro | `contentforge config set gemini_api_key YOUR_KEY` |
| **Ollama** | llama3.2, mistral, phi3 (local) | Just have Ollama running locally |

```bash
# Switch default provider
contentforge config set default_provider gemini

# Use a specific provider for one command
contentforge generate blog --topic "AI" --provider ollama --model mistral
```

## Common Options

All `generate` commands support these options:

| Option | Description |
|--------|-------------|
| `--provider / -p` | LLM provider (openai/gemini/ollama) |
| `--model / -m` | Model override |
| `--output / -o` | Save output to file |
| `--format / -f` | Output format (markdown/plain/json) |
| `--copy` | Copy result to clipboard |
| `--stream / --no-stream` | Enable/disable streaming |
| `--temperature` | Sampling temperature (0.0-2.0) |
| `--max-tokens` | Maximum output tokens |

## Configuration

```bash
# Show current config
contentforge config

# Set a value
contentforge config set default_provider gemini
contentforge config set default_temperature 0.5

# Show config file path
contentforge config path
```

Configuration is stored in `~/.contentforge/config.toml`. Environment variables override config file values using the `CONTENTFORGE_` prefix:

```bash
export CONTENTFORGE_OPENAI_API_KEY=sk-your-key
export CONTENTFORGE_DEFAULT_PROVIDER=gemini
```

## Templates

```bash
# List all templates
contentforge templates

# Show template details
contentforge templates show blog
```

## Development

```bash
git clone https://github.com/brolyroly007/contentforge.git
cd contentforge
make dev        # Install with dev dependencies
make test       # Run tests
make lint       # Run linter
make format     # Auto-format code
```

## License

MIT
