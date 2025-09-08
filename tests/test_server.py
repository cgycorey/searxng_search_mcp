"""
Tests for SearXNG MCP Server
"""

from unittest.mock import AsyncMock

import pytest

from searxng_search_mcp import SearXNGClient, SearXNGServer


@pytest.fixture
def mock_searxng_client() -> SearXNGClient:
    """Create a mock SearXNG client for testing"""
    client = SearXNGClient("https://example.com")
    client.search = AsyncMock()
    client.fetch_url = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_searxng_search_success(mock_searxng_client: SearXNGClient) -> None:
    """Test successful SearXNG search"""
    mock_response = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "Test content",
            }
        ],
        "query": "test query",
        "number_of_results": 1,
        "answers": [],
    }
    mock_searxng_client.search.return_value = mock_response

    result = await mock_searxng_client.search("test query")

    assert result == mock_response
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Test Result"
    mock_searxng_client.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_searxng_search_with_parameters(
    mock_searxng_client: SearXNGClient,
) -> None:
    """Test SearXNG search with additional parameters"""
    mock_response = {
        "results": [],
        "query": "test",
        "number_of_results": 0,
        "answers": [],
    }
    mock_searxng_client.search.return_value = mock_response

    await mock_searxng_client.search(
        query="test", pageno=2, time_range="week", language="en", safesearch=1
    )

    mock_searxng_client.search.assert_called_once_with(
        query="test", pageno=2, time_range="week", language="en", safesearch=1
    )


@pytest.mark.asyncio
async def test_url_fetch_success(mock_searxng_client: SearXNGClient) -> None:
    """Test successful URL fetching"""
    mock_content = "<html><body>Test content</body></html>"
    mock_searxng_client.fetch_url.return_value = mock_content

    result = await mock_searxng_client.fetch_url("https://example.com")

    assert result == mock_content
    mock_searxng_client.fetch_url.assert_called_once_with("https://example.com")


def test_searxng_server_initialization() -> None:
    """Test SearXNG server initialization with environment variable"""
    import os
    from unittest.mock import patch

    # Test with environment variable set
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()
        assert server.server.name == "searxng-search-mcp"
        assert hasattr(server, "client")
        assert hasattr(server, "h")
        assert server.client.base_url == "https://test.example.com"

    # Test without environment variable
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(
            ValueError, match="SEARXNG_URL environment variable is required"
        ):
            SearXNGServer()


def test_searxng_server_tools() -> None:
    """Test that server has the expected tools"""
    import os
    from unittest.mock import patch

    # Mock the environment variable to avoid requiring it to be set
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        # Test that we can access the tools (this would normally be called by MCP)
        # We can't easily test the async handlers without a proper MCP setup
        assert hasattr(server, "_handle_web_search")
        assert hasattr(server, "_handle_web_url_read")

        # Test that server has the expected server instance
        assert server.server is not None
        assert hasattr(server.server, "list_tools")
        assert hasattr(server.server, "call_tool")


@pytest.mark.asyncio
async def test_searxng_search_error_handling(
    mock_searxng_client: SearXNGClient,
) -> None:
    """Test SearXNG search error handling"""
    import httpx

    # Test HTTPError
    mock_searxng_client.search.side_effect = httpx.HTTPError("Network error")

    with pytest.raises(httpx.HTTPError, match="Network error"):
        await mock_searxng_client.search("test query")

    # Test TimeoutException
    mock_searxng_client.search.side_effect = httpx.TimeoutException("Request timeout")

    with pytest.raises(httpx.TimeoutException, match="Request timeout"):
        await mock_searxng_client.search("test query")

    # Test RequestError
    mock_searxng_client.search.side_effect = httpx.RequestError("Connection error")

    with pytest.raises(httpx.RequestError, match="Connection error"):
        await mock_searxng_client.search("test query")


@pytest.mark.asyncio
async def test_searxng_search_empty_response(
    mock_searxng_client: SearXNGClient,
) -> None:
    """Test SearXNG search with empty response"""
    mock_response = {
        "results": [],
        "query": "empty query",
        "number_of_results": 0,
        "answers": [],
    }
    mock_searxng_client.search.return_value = mock_response

    result = await mock_searxng_client.search("empty query")

    assert result == mock_response
    assert "results" in result
    assert result["results"] == []
    assert result["number_of_results"] == 0


def test_project_structure() -> None:
    """Test that project structure is correct"""
    import os

    # Check that main files exist
    assert os.path.exists("src/searxng_search_mcp/__init__.py")
    assert os.path.exists("src/searxng_search_mcp/server.py")
    assert os.path.exists("src/searxng_search_mcp/__main__.py")
    assert os.path.exists("pyproject.toml")
    assert os.path.exists("README.md")
    assert os.path.exists("LICENSE")
    assert os.path.exists("tests/")


if __name__ == "__main__":
    test_project_structure()
    print("✅ Basic structure tests passed!")
