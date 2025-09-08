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
- Make sure you clean the cache of uv first before building

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

# MCP Web Search Usage Rules
- Use the `metasearch_web` tool when user requests web search functionality
- Use the `fetch_web_content` tool when user requests to fetch and parse web page content
- Default to markdown format for web content unless user specifies otherwise
- Apply time range filters when user requests recent or time-specific information
- Use language filters when user requests results in specific languages
- Set appropriate safesearch levels based on content requirements
- Handle search errors gracefully and provide informative error messages