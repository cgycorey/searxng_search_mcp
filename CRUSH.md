# Build/Test/Lint Commands
- Test single file: `uv run pytest tests/test_server.py -v`
- Test single function: `uv run pytest tests/test_server.py::test_searxng_search_success -v`
- Run all tests: `uv run pytest -v`
- Format code: `uv run black src/ tests/`
- Sort imports: `uv run isort src/ tests/`
- Lint: `uv run ruff check src/ tests/ --fix`
- Type check: `uv run mypy src/`
- Run all checks: `uv run black . && uv run isort . && uv run ruff check . --fix && uv run mypy src/ && uv run pytest`
- Build package: `uv build`
- Make sure you clean the cache of uv first before building

# Code Style Guidelines
- Use Black formatter with 88-character line length
- Use isort for import sorting with Black profile
- Type hints required for all function signatures
- Use snake_case for variables and functions, PascalCase for classes
- Use async/await for all HTTP operations
- Handle exceptions gracefully with try/catch blocks
- Use httpx for HTTP requests with configurable timeout (SEARXNG_TIMEOUT env var)
- Follow strict mypy configuration (no untyped code allowed)
- Use pytest for testing with @pytest.mark.asyncio for async tests

# MCP Web Search Usage Rules
- Use the `metasearch_web` tool when user requests web search functionality
- Use the `fetch_web_content` tool when user requests to fetch and parse web page content, and also get the links from search results above
- Default to markdown format for web content unless user specifies otherwise
- Apply time range filters when user requests recent or time-specific information
- Use language filters when user requests results in specific languages
- Set appropriate safesearch levels based on content requirements
- Handle search errors gracefully and provide informative error messages

# New Features Added
- Configurable timeout via SEARXNG_TIMEOUT environment variable (default: 120s)
- Content size limits via SEARXNG_MAX_CONTENT_SIZE environment variable (default: 10MB)
- URL validation to prevent SSRF attacks
- Shared utilities module (utils.py) to eliminate code duplication
- Enhanced error handling with specific exception types
- Improved logging configuration with stderr support for MCP compatibility