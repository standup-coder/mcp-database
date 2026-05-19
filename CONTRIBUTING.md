# Contributing to MCP Tool Suite

Thank you for your interest in contributing to MCP Tool Suite! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Redis (for Celery)
- Git

### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/mcp4coder.git
   cd mcp4coder
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r config/requirements.txt
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

6. Copy environment file:
   ```bash
   cp config/.env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Write tests for new functionality
4. Run tests:
   ```bash
   pytest tests/ -v
   ```

5. Run linting:
   ```bash
   flake8 app
   mypy app --ignore-missing-imports
   ```

6. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a Pull Request

## Code Style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://github.com/pycqa/isort) for import sorting
- Maximum line length: 88 characters
- Use type hints for all function signatures

### Formatting

```bash
# Format code with Black
black app tests

# Sort imports with isort
isort app tests

# Check formatting
black --check app tests
isort --check-only app tests
```

### Type Checking

```bash
mypy app --ignore-missing-imports
```

## Testing

### Writing Tests

- Write tests for all new functionality
- Use pytest for testing
- Use fixtures for common test data
- Mock external dependencies

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mcp.py -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run only unit tests
pytest tests/ -v -m unit

# Run only integration tests
pytest tests/ -v -m integration
```

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_mcp.py          # MCP module tests
├── test_integration.py  # Integration tests
├── test_security.py     # Security tests
├── test_e2e.py          # End-to-end tests
└── test_utils.py        # Utility tests
```

## Submitting Changes

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(mcp): add new weather server
fix(auth): resolve JWT token validation issue
docs(readme): update installation instructions
test(security): add rate limiter tests
```

### Pull Request Guidelines

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Keep PRs focused and small
6. Describe your changes in the PR description

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. Description of the issue
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment details (OS, Python version, etc.)
6. Error messages or logs

### Feature Requests

When requesting features, please include:

1. Description of the feature
2. Use case
3. Proposed implementation (if any)
4. Alternatives considered

## Adding New MCP Servers

To add a new MCP server:

1. Create a new file in `app/mcp/servers/`:
   ```python
   from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability
   
   class YourServerMCPServer(BaseMCPServer):
       def register_tools(self):
           # Register your tools
           pass
       
       def register_resources(self):
           # Register your resources
           pass
       
       async def execute_tool(self, tool_name: str, params: dict):
           # Implement tool execution
           pass
       
       async def _read_resource_content(self, resource):
           # Implement resource reading
           pass
   ```

2. Add server type to `ServerType` enum in `app/mcp/server_factory.py`
3. Add server configuration to `_load_builtin_servers()` method
4. Add tests in `tests/test_mcp.py`
5. Update documentation

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing! 🎉
