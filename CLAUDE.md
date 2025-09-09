# Claude Code Assistant Guidelines

## Project Overview

This is a SearXNG Search MCP (Model Context Protocol) server that provides web search capabilities through the Model Context Protocol. It enables Claude to perform web searches and fetch web content using SearXNG instances.

## Development Commands

### Testing
- **Test single file:** `uv run pytest tests/test_server.py -v`
- **Test single function:** `uv run pytest tests/test_server.py::test_searxng_search_success -v`
- **Run all tests:** `uv run pytest -v`

### Code Quality
- **Format code:** `uv run black src/ tests/`
- **Sort imports:** `uv run isort src/ tests/`
- **Lint code:** `uv run ruff check src/ tests/`
- **Type check:** `uv run mypy src/`
- **Run all checks:** `uv run black . && uv run isort . && uv run ruff check . && uv run mypy . && uv run pytest`

### Build & Deployment
- **Build package:** `uv build`
- **Clean cache before building:** `uv cache clean`

### Install Dependencies
- **Install project dependencies:** `uv sync`
- **Install development dependencies:** `uv sync --group dev`

## Code Style Guidelines

### Core Principles
- Use `uv` to run all commands and dependencies
- **Dependency Management:** Always use `uv sync` to install/update dependencies
- **Formatting:** Black formatter with 88-character line length
- **Imports:** isort with Black profile
- **Type Safety:** Type hints required for all function signatures
- **Naming:** `snake_case` for variables and functions, `PascalCase` for classes

### Architecture Patterns
- **Asynchronous Operations:** Use async/await for all HTTP operations
- **Error Handling:** Handle exceptions gracefully with try/catch blocks
- **HTTP Client:** Use httpx with 120s timeout for all HTTP requests
- **Type Checking:** Follow strict mypy configuration (no untyped code allowed)
- **Testing:** Use `uv run pytest` with `@pytest.mark.asyncio` for async tests

## Key Files

### Source Code
- `src/searxng_search_mcp/client.py` - HTTP client for SearXNG communication
- `src/searxng_search_mcp/server.py` - MCP server implementation
- `src/searxng_search_mcp/server_main.py` - Main entry point

### Testing
- `tests/` - Comprehensive test suite with full coverage

## MCP Web Search Usage Rules

### Tool Selection
- Use `metasearch_web` when user requests web search functionality
- Use `fetch_web_content` when user requests to fetch and parse web page content

### Content Handling
- Default to markdown format for web content unless user specifies otherwise
- Apply time range filters when user requests recent or time-specific information
- Use language filters when user requests results in specific languages
- Set appropriate safesearch levels based on content requirements

### Error Management
- Handle search errors gracefully
- Provide informative error messages
- Implement fallback mechanisms when available

## Dependencies

### Core Runtime
- `mcp` - Model Context Protocol framework
- `httpx` - HTTP client library
- `beautifulsoup4` - HTML parsing
- `html2text` - HTML to text conversion

### Development Tools
- `pytest` - Testing framework
- `black` - Code formatter
- `isort` - Import sorter
- `ruff` - Linter
- `mypy` - Type checker

## Testing Strategy

### Test Categories
- **Unit Tests:** Individual component testing
- **Integration Tests:** MCP server functionality testing
- **Error Handling:** Edge case and error scenario testing
- **Performance Tests:** Search operation performance testing
- **Mock Testing:** External HTTP request mocking

## Debugging Practices

### Common Issues
- **Connection Timeouts:** Check SearXNG instance availability and network connectivity
- **SSL Certificate Errors:** Verify SSL certificates or use HTTP for testing
- **Rate Limiting:** Implement retry logic with exponential backoff
- **Parse Errors:** Validate HTML structure changes in target websites

### Debug Commands
- **Enable verbose logging:** Set `LOG_LEVEL=DEBUG` environment variable
- **Test SearXNG instance:** `curl -I https://your-searxng-instance.com`
- **Check MCP server logs:** Monitor output during server startup and operation

### Best Practices
- Maintain high test coverage across all components
- Test both success and failure scenarios
- Mock external dependencies to ensure reliable testing
- Include performance benchmarks for critical operations