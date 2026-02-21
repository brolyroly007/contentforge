# Contributing to ContentForge

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/brolyroly007/contentforge.git
cd contentforge
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
make dev
```

## Running Tests

```bash
make test       # Run all tests
make test-cov   # Run with coverage
make lint       # Check linting
make format     # Auto-format
```

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run `make lint` and `make test`
5. Commit and push
6. Open a pull request

## Adding a New Template

1. Add the template definition in `src/contentforge/templates/registry.py`
2. Add a corresponding subcommand in `src/contentforge/commands/generate.py`
3. Add tests in `tests/test_templates.py`

## Adding a New Provider

1. Create `src/contentforge/providers/your_provider.py` implementing `BaseProvider`
2. Register it in `src/contentforge/providers/__init__.py`
3. Add config fields in `src/contentforge/config.py`
4. Add tests in `tests/test_providers.py`
