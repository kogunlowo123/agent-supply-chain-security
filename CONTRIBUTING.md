# Contributing

## Development Setup

```bash
git clone https://github.com/kogunlowo123/agent-supply-chain-security.git
cd agent-supply-chain-security
pip install uv
make install
pre-commit install
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes following the code style
3. Write tests for new functionality
4. Run tests: `make test`
5. Run linting: `make lint`
6. Submit a pull request

## Code Style

- Python: PEP 8, enforced by ruff
- Type hints required
- Docstrings required for public APIs
- No placeholders or TODOs in production code

## Testing

- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Security tests: `pytest tests/security/`
- Coverage minimum: 80%

## Architecture

Domain-Driven Design (DDD) with hexagonal architecture.
