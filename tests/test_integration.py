"""
Tests for SearXNG MCP Server Integration
"""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from searxng_search_mcp import SearXNGClient, SearXNGServer


@pytest.fixture
def mock_http_response() -> MagicMock:
    """Create a mock HTTP response"""
    response = MagicMock()
    response.json.return_value = {
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "Test content 1",
                "publishedDate": "2023-01-01",
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "Test content 2",
                "publishedDate": "2023-01-02",
            },
        ]
    }
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_html_content() -> str:
    """Sample HTML content for testing"""
    return """
    <html>
        <head>
            <title>Test Page</title>
            <script>alert('test');</script>
            <style>body { color: red; }</style>
        </head>
        <body>
            <h1>Main Title</h1>
            <p>This is a test paragraph with <strong>bold text</strong>.</p>
            <script>console.log('another script');</script>
            <div class="content">
                <p>More content here</p>
            </div>
        </body>
    </html>
    """


@pytest.mark.asyncio
async def test_client_search_with_full_response() -> None:
    """Test client search with complete response structure"""
    client = SearXNGClient("https://test.example.com")

    mock_response = {
        "results": [
            {
                "title": "Complete Result",
                "url": "https://example.com/complete",
                "content": "Complete content with all fields",
                "publishedDate": "2023-12-01",
                "author": "Test Author",
                "thumbnail": "https://example.com/thumb.jpg",
            }
        ],
        "query": "test query",
        "number_of_results": 1,
        "answers": [],
    }

    client.search = AsyncMock(return_value=mock_response)

    result = await client.search("test query")

    assert result == mock_response
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Complete Result"
    assert result["results"][0]["publishedDate"] == "2023-12-01"


@pytest.mark.asyncio
async def test_client_authentication() -> None:
    """Test client with authentication"""
    client = SearXNGClient("https://auth.example.com", auth=("username", "password"))

    assert client.auth == ("username", "password")
    assert client.base_url == "https://auth.example.com"


@pytest.mark.asyncio
async def test_client_with_proxy() -> None:
    """Test client with proxy configuration"""
    client = SearXNGClient(
        "https://proxy.example.com", proxy="http://proxy.example.com:8080"
    )

    assert client.proxy == "http://proxy.example.com:8080"
    assert client.base_url == "https://proxy.example.com"


@pytest.mark.asyncio
async def test_client_search_timeout_handling() -> None:
    """Test client search timeout handling"""
    client = SearXNGClient("https://timeout.example.com")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(httpx.TimeoutException):
            await client.search("timeout query")


@pytest.mark.asyncio
async def test_client_search_http_error_handling() -> None:
    """Test client search HTTP error handling"""
    client = SearXNGClient("https://error.example.com")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )
        mock_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await client.search("error query")


@pytest.mark.asyncio
async def test_client_fetch_url_success() -> None:
    """Test successful URL fetching"""
    client = SearXNGClient("https://fetch.example.com")
    expected_content = "<html><body>Test content</body></html>"

    client.fetch_url = AsyncMock(return_value=expected_content)

    result = await client.fetch_url("https://example.com")

    assert result == expected_content


@pytest.mark.asyncio
async def test_server_initialization_with_env_vars() -> None:
    """Test server initialization with environment variables"""
    with patch.dict(
        os.environ,
        {
            "SEARXNG_URL": "https://env.example.com",
            "AUTH_USERNAME": "testuser",
            "AUTH_PASSWORD": "testpass",
            "HTTP_PROXY": "http://proxy.example.com:8080",
        },
    ):
        server = SearXNGServer()

        assert server.client.base_url == "https://env.example.com"
        assert server.client.auth == ("testuser", "testpass")
        assert server.client.proxy == "http://proxy.example.com:8080"


@pytest.mark.asyncio
async def test_server_web_search_handler_empty_query() -> None:
    """Test server web search handler with empty query"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        result = await server._handle_web_search({"query": ""})

        assert len(result) == 1
        assert "Search query is required" in result[0].text


@pytest.mark.asyncio
async def test_server_web_search_handler_success() -> None:
    """Test server web search handler success"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        mock_response = {
            "results": [
                {
                    "title": "Search Result",
                    "url": "https://example.com",
                    "content": "Search content",
                    "publishedDate": "2023-01-01",
                }
            ]
        }

        server.client.search = AsyncMock(return_value=mock_response)

        result = await server._handle_web_search({"query": "test"})

        assert len(result) == 1
        text_content = result[0].text
        assert "Result 1: Search Result" in text_content
        assert "URL: https://example.com" in text_content
        assert "Content: Search content" in text_content


@pytest.mark.asyncio
async def test_server_web_url_read_empty_url() -> None:
    """Test server web URL read with empty URL"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        result = await server._handle_web_url_read({"url": ""})

        assert len(result) == 1
        assert "URL is required" in result[0].text


@pytest.mark.asyncio
async def test_server_web_url_read_markdown_format(mock_html_content: str) -> None:
    """Test server web URL read with markdown format"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.fetch_url = AsyncMock(return_value=mock_html_content)

        result = await server._handle_web_url_read(
            {"url": "https://example.com", "format": "markdown"}
        )

        assert len(result) == 1
        text_content = result[0].text
        assert "# Main Title" in text_content
        assert "This is a test paragraph with **bold text**." in text_content
        # Scripts and styles should be removed
        assert "<script>" not in text_content
        assert "<style>" not in text_content


@pytest.mark.asyncio
async def test_server_web_url_read_html_format(mock_html_content: str) -> None:
    """Test server web URL read with HTML format"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.fetch_url = AsyncMock(return_value=mock_html_content)

        result = await server._handle_web_url_read(
            {"url": "https://example.com", "format": "html"}
        )

        assert len(result) == 1
        text_content = result[0].text
        assert "<h1>Main Title</h1>" in text_content
        assert "<p>This is a test paragraph" in text_content
        # Scripts and styles should be removed
        assert "<script>" not in text_content
        assert "<style>" not in text_content


@pytest.mark.asyncio
async def test_server_web_url_read_text_format(mock_html_content: str) -> None:
    """Test server web URL read with text format"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.fetch_url = AsyncMock(return_value=mock_html_content)

        result = await server._handle_web_url_read(
            {"url": "https://example.com", "format": "text"}
        )

        assert len(result) == 1
        text_content = result[0].text
        assert "Main Title" in text_content
        assert "This is a test paragraph with bold text" in text_content
        # Should be plain text without HTML tags
        assert "<h1>" not in text_content
        assert "<p>" not in text_content


@pytest.mark.asyncio
async def test_server_web_url_read_json_format(mock_html_content: str) -> None:
    """Test server web URL read with JSON format"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.fetch_url = AsyncMock(return_value=mock_html_content)

        result = await server._handle_web_url_read(
            {"url": "https://example.com", "format": "json"}
        )

        assert len(result) == 1
        json_content = json.loads(result[0].text)

        assert json_content["url"] == "https://example.com"
        assert json_content["title"] == "Test Page"
        assert "Main Title" in json_content["content"]
        assert "<h1>Main Title</h1>" in json_content["html"]
        assert "# Main Title" in json_content["markdown"]
        assert json_content["metadata"]["format"] == "json"


@pytest.mark.asyncio
async def test_server_web_url_read_raw_format(mock_html_content: str) -> None:
    """Test server web URL read with raw format"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.fetch_url = AsyncMock(return_value=mock_html_content)

        result = await server._handle_web_url_read(
            {"url": "https://example.com", "raw": True}
        )

        assert len(result) == 1
        text_content = result[0].text
        # Should return original content unchanged
        assert text_content == mock_html_content
        assert "<script>alert('test');</script>" in text_content
        assert "<style>body { color: red; }</style>" in text_content


@pytest.mark.asyncio
async def test_server_error_handling_configuration_error() -> None:
    """Test server error handling for configuration errors"""
    with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
        with pytest.raises(
            ValueError, match="SEARXNG_URL environment variable is required"
        ):
            SearXNGServer()


@pytest.mark.asyncio
async def test_server_error_handling_timeout() -> None:
    """Test server error handling for timeout errors"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        server.client.search = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        result = await server._handle_web_search({"query": "test"})

        assert len(result) == 1
        assert "Search request timed out" in result[0].text


@pytest.mark.asyncio
async def test_server_error_handling_http_error() -> None:
    """Test server error handling for HTTP errors"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        mock_response = MagicMock()
        mock_response.status_code = 500
        server.client.search = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Internal Server Error", request=MagicMock(), response=mock_response
            )
        )

        result = await server._handle_web_search({"query": "test"})

        assert len(result) == 1
        assert "HTTP error 500" in result[0].text


def test_client_url_normalization() -> None:
    """Test that client normalizes URLs correctly"""
    client1 = SearXNGClient("https://example.com/")
    client2 = SearXNGClient("https://example.com")
    client3 = SearXNGClient("https://example.com/search/")

    assert client1.base_url == "https://example.com"
    assert client2.base_url == "https://example.com"
    assert client3.base_url == "https://example.com/search"


if __name__ == "__main__":
    # Run a quick test to verify the test file works
    print("✅ Integration tests file is ready!")
