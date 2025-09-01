# Copilot Guidelines

These rules help GitHub Copilot work correctly in this repo.

## Environment

- Use **uv** for dependencies and running scripts.
- Do **not** suggest `pip`, `poetry`, `conda`, `requirements.txt`, or `setup.py`.
- All dependencies go into `pyproject.toml`.

## Files

- Never create new files unless explicitly asked.
- Never generate: `requirements.txt`, `setup.py`, `Pipfile*`, `.python-version`, `poetry.lock`.

## Code

- Language: Python 3, follow PEP 8.
- Prefer small, typed functions with clear interfaces.
- Do **not** add extra methods or functions unless explicitly needed.
- Use `pytest` for tests (`uv run pytest`).

## Testing

- Write tests only when explicitly requested.
- Create one test file per source file (e.g., `test_module.py` for `module.py`).
- Use `pytest` with clear, descriptive test names (e.g., `test_parse_config_with_invalid_json_raises_error`).
- Focus on testing public interfaces and edge cases.
- Keep test files in `tests/` directory with `test_` prefix.
- Prefer integration tests over unit tests for glue code requiring extensive mocking.

## Comments

- Generally never add comments to generated code.
- Avoid explaining what the code is doing; the code should be self-explanatory.
- Only add comments to clarify complex logic or important details.

## Docs

- Only add docstrings to public functions and classes when useful.
- Do **not** add redundant or obvious comments.
