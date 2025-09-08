# Build/Test/Lint Commands
- Test single file: `pytest tests/test_server.py -v`
- Test single function: `pytest tests/test_server.py::test_searxng_search_success -v`
- Run all tests: `pytest -v`
- Format code: `black src/ tests/`
- Sort imports: `isort src/ tests/`
- Lint: `ruff check src/ tests/`
- Type check: `mypy src/`
- Run all checks: `black . && isort . && ruff check . && mypy . && pytest`
- Build package: `uv build`

# Code Style Guidelines
- Use Black formatter with 88-character line length
- Use isort for import sorting with Black profile
- Type hints required for all function signatures
- Use snake_case for variables and functions, PascalCase for classes
- Use async/await for all HTTP operations
- Handle exceptions gracefully with try/catch blocks
- Use httpx for HTTP requests with 120s timeout
- Follow strict mypy configuration (no untyped code allowed)
- Use pytest for testing with @pytest.mark.asyncio for async tests