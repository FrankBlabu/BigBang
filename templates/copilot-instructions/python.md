<!--
#
# python.md - Python-specific coding rules for AI agents
#
# This file contains Python-specific best practices and requirements.
# It is used in combination with base.md for Python projects.
#
-->

# Python

- When using Python, always use a strong type system, such as `pydantic`, to ensure that all data structures are well-defined and validated.
- Always use a virtual environment for Python projects to manage dependencies and avoid conflicts.
- Follow the PEP 8 style guide for Python code to ensure consistency and readability.
- Use type hints consistently throughout the codebase.

## Python-specific patterns

- The UUID class must be referenced via the `UUID()` expression, not via the full module path `uuid.UUID()`. This implies a correct import: `from uuid import UUID`.

## Testing

- Use `pytest` as the testing framework for Python projects.
- Use `pytest-cov` for code coverage reporting.
- Use `pytest-mock` for mocking in tests.

## Code Quality

- Use `ruff` for linting and code formatting.
- Use `mypy` for static type checking.
- Ensure all type checking passes with strict mode enabled.
