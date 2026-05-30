# Contributing to Smart Irrigation

## Development Setup

### Prerequisites
- Python 3.13 or higher
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/JustChr/HAsmartirrigation.git
   cd HAsmartirrigation
   ```

2. **Set up development environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Linux/macOS
   pip install -r requirements-dev.txt
   ```

### Running Tests

```bash
pytest tests/ -v
pytest custom_components/smart_irrigation/tests/ -v
```

### Code Quality

```bash
black custom_components/smart_irrigation/          # Format
ruff check custom_components/smart_irrigation/     # Lint
```

### Bumping the Version

```bash
make bump VERSION=vYYYY.MM.NN
```

Updates `manifest.json`, `frontend/package.json`, and `const.py` in one step.
Rebuild the frontend afterwards to apply.

## Project Structure

```
custom_components/smart_irrigation/   Main component code
tests/                                Unit tests (run with coverage in CI)
custom_components/.../tests/          Integration tests (run in CI)
automations/                          Example HA automation YAML files
blueprints/                           HA blueprint YAML files
docs/                                 Jekyll documentation site
```
