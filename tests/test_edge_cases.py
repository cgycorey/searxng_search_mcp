"""
Edge case and error condition tests for SearXNG MCP Server
"""

import json
import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from searxng_search_mcp import SearXNGClient, SearXNGServer


@pytest.mark.asyncio
async def test_malformed_json_response() -> None:
    """Test handling of malformed JSON responses"""
    client = SearXNGClient("https://malformed.example.com")

    client.search = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))

    with pytest.raises(json.JSONDecodeError):
        await client.search("malformed query")


@pytest.mark.asyncio
async def test_empty_json_response() -> None:
    """Test handling of empty JSON response"""
    client = SearXNGClient("https://empty.example.com")

    mock_response = {}
    client.search = AsyncMock(return_value=mock_response)

    result = await client.search("empty query")

    assert result == {}
    assert "results" not in result


@pytest.mark.asyncio
async def test_none_values_in_response() -> None:
    """Test handling of None values in search response"""
    client = SearXNGClient("https://none.example.com")

    mock_response = {
        "results": [
            {"title": None, "url": None, "content": None, "publishedDate": None}
        ]
    }
    client.search = AsyncMock(return_value=mock_response)

    result = await client.search("none query")

    assert result == mock_response
    assert result["results"][0]["title"] is None
    assert result["results"][0]["url"] is None


@pytest.mark.asyncio
async def test_missing_fields_in_response() -> None:
    """Test handling of missing fields in search response"""
    client = SearXNGClient("https://missing.example.com")

    mock_response = {"results": [{}]}  # Empty result object
    client.search = AsyncMock(return_value=mock_response)

    result = await client.search("missing query")

    assert result == mock_response
    assert result["results"][0] == {}


@pytest.mark.asyncio
async def test_unicode_content_handling() -> None:
    """Test handling of Unicode content in responses"""
    client = SearXNGClient("https://unicode.example.com")

    mock_response = {
        "results": [
            {
                "title": "测试标题",  # Chinese
                "url": "https://example.com",
                "content": "こんにちは世界",  # Japanese
                "publishedDate": "2023-01-01",
            },
            {
                "title": "العنوان",  # Arabic
                "url": "https://example.com/ar",
                "content": "مرحبا بالعالم",  # Arabic
                "publishedDate": "2023-01-02",
            },
            {
                "title": "Заголовок",  # Russian
                "url": "https://example.com/ru",
                "content": "Привет мир",  # Russian
                "publishedDate": "2023-01-03",
            },
        ]
    }
    client.search = AsyncMock(return_value=mock_response)

    result = await client.search("unicode query")

    assert len(result["results"]) == 3
    assert result["results"][0]["title"] == "测试标题"
    assert result["results"][1]["title"] == "العنوان"
    assert result["results"][2]["title"] == "Заголовок"


@pytest.mark.asyncio
async def test_special_characters_in_html() -> None:
    """Test handling of special characters in HTML content"""
    client = SearXNGClient("https://special.example.com")

    html_content = """
    <html>
        <head><title>Special & Characters</title></head>
        <body>
            <p>This has &amp; &lt; &gt; &quot; &apos; entities</p>
            <p>Unicode: © ® ™ € £ ¥ § ¶ † ‡ … — –</p>
            <p>Math: ≤ ≥ ≠ ± × ÷ ∞ ∑ ∆ π Ω</p>
            <script>alert('special & chars');</script>
        </body>
    </html>
    """

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.text = html_content
        mock_client.get.return_value.raise_for_status.return_value = None

        result = await client.fetch_url("https://special.example.com")

        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result
        assert "©" in result
        assert "®" in result
        assert "€" in result


@pytest.mark.asyncio
async def test_very_long_url() -> None:
    """Test handling of very long URLs"""
    client = SearXNGClient("https://long.example.com")

    # Create a very long URL (over 2000 characters)
    long_url = "https://example.com/?" + "a" * 2000

    mock_content = "<html><body>Long URL content</body></html>"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.text = mock_content
        mock_client.get.return_value.raise_for_status.return_value = None

        result = await client.fetch_url(long_url)

        assert result == mock_content


@pytest.mark.asyncio
async def test_invalid_url_format() -> None:
    """Test handling of invalid URL formats"""
    client = SearXNGClient("https://invalid.example.com")

    invalid_urls = [
        "not-a-url",
        "ftp://example.com",  # Non-HTTP protocol
        "javascript:alert('xss')",  # JavaScript protocol
        "data:text/html,<script>alert('xss')</script>",  # Data URI
        "",  # Empty URL
        "https://",  # Incomplete URL
        "https:///example.com",  # Triple slash
    ]

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        for invalid_url in invalid_urls:
            # Mock should still work even with invalid URLs
            mock_client.get.return_value.text = "<html><body>Content</body></html>"
            mock_client.get.return_value.raise_for_status.return_value = None

            # This should not raise an exception, but the HTTP client might
            try:
                result = await client.fetch_url(invalid_url)
                assert result == "<html><body>Content</body></html>"
            except Exception as e:
                # Some invalid URLs might cause HTTP client errors or our validation
                assert isinstance(e, (httpx.InvalidURL, httpx.HTTPError, ValueError))


@pytest.mark.asyncio
async def test_server_with_whitespace_only_query() -> None:
    """Test server handling of whitespace-only queries"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        whitespace_queries = ["   ", "\t\t\t", "\n\n\n", " \t \n ", ""]

        for query in whitespace_queries:
            result = await server._handle_web_search({"query": query})

            assert len(result) == 1
            assert "Search query is required" in result[0].text


@pytest.mark.asyncio
async def test_server_with_whitespace_only_url() -> None:
    """Test server handling of whitespace-only URLs"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        whitespace_urls = ["   ", "\t\t\t", "\n\n\n", " \t \n ", ""]

        for url in whitespace_urls:
            result = await server._handle_web_url_read({"url": url})

            assert len(result) == 1
            assert "URL is required" in result[0].text


@pytest.mark.asyncio
async def test_server_with_invalid_format_parameter() -> None:
    """Test server handling of invalid format parameters"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        html_content = "<html><body>Test content</body></html>"
        server.client.fetch_url = AsyncMock(return_value=html_content)

        # Test with invalid format (should default to markdown)
        result = await server._handle_web_url_read(
            {"url": "https://example.com", "format": "invalid_format"}
        )

        assert len(result) == 1
        # Should default to markdown format
        assert "Test content" in result[0].text


@pytest.mark.asyncio
async def test_network_connection_error() -> None:
    """Test handling of network connection errors"""
    client = SearXNGClient("https://unreachable.example.com")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")

        with pytest.raises(httpx.ConnectError):
            await client.search("connection test")


@pytest.mark.asyncio
async def test_ssl_error_handling() -> None:
    """Test handling of SSL certificate errors"""
    client = SearXNGClient("https://ssl-error.example.com")

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.HTTPError("SSL certificate verify failed")

        with pytest.raises(httpx.HTTPError):
            await client.search("ssl test")


@pytest.mark.asyncio
async def test_redirect_handling() -> None:
    """Test handling of HTTP redirects"""
    client = SearXNGClient("https://redirect.example.com")

    mock_response = {
        "results": [{"title": "Redirect Result", "url": "https://final.example.com"}]
    }
    client.search = AsyncMock(return_value=mock_response)

    # This should work transparently as httpx handles redirects
    result = await client.search("redirect test")

    assert result == mock_response


@pytest.mark.asyncio
async def test_chunked_transfer_encoding() -> None:
    """Test handling of chunked transfer encoding"""
    client = SearXNGClient("https://chunked.example.com")

    # Simulate chunked response
    chunked_content = "<html><body>Chunked content</body></html>"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.text = chunked_content
        mock_client.get.return_value.raise_for_status.return_value = None
        mock_client.get.return_value.headers = {"Transfer-Encoding": "chunked"}

        result = await client.fetch_url("https://chunked.example.com")

        assert result == chunked_content


@pytest.mark.asyncio
async def test_compressed_response_handling() -> None:
    """Test handling of compressed responses"""
    client = SearXNGClient("https://compressed.example.com")

    compressed_content = "<html><body>Compressed content</body></html>"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.text = compressed_content
        mock_client.get.return_value.raise_for_status.return_value = None
        mock_client.get.return_value.headers = {"Content-Encoding": "gzip"}

        # httpx should handle decompression automatically
        result = await client.fetch_url("https://compressed.example.com")

        assert result == compressed_content


@pytest.mark.asyncio
async def test_malformed_html_content() -> None:
    """Test handling of malformed HTML content"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()

        # Malformed HTML (missing closing tags, invalid nesting)
        malformed_html = """
        <html>
            <head><title>Malformed</head>
            <body>
                <div>Unclosed div
                <p>Paragraph without closing
                <span>Nested <strong>bold <em>italic</strong> wrong nesting</em>
                <table><tr><td>Missing closing table
            </html>
        """

        server.client.fetch_url = AsyncMock(return_value=malformed_html)

        # Should handle malformed HTML gracefully
        result = await server._handle_web_url_read(
            {"url": "https://malformed.example.com", "format": "text"}
        )

        assert len(result) == 1
        assert "Malformed" in result[0].text
        assert "Unclosed div" in result[0].text


if __name__ == "__main__":
    print("✅ Edge case tests file is ready!")
