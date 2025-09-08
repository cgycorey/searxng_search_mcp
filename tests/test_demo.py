#!/usr/bin/env python3
"""
Example usage and tests for SearXNG Search MCP Server
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


@pytest.fixture
def mock_server() -> SearXNGServer:
    """Create a mock SearXNG server for testing"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        with patch("searxng_search_mcp.server.SearXNGClient") as mock_client_class:
            # Create a mock client instance
            mock_client_instance = mock_client_class.return_value
            mock_client_instance.search = AsyncMock()
            mock_client_instance.fetch_url = AsyncMock()

            # Create server with mocked client
            server = SearXNGServer()
            server.client = mock_client_instance
            return server


@pytest.mark.asyncio
async def test_search_functionality(mock_server: SearXNGServer) -> None:
    """Test basic search functionality with multiple results"""
    mock_search_response = {
        "results": [
            {
                "title": "AI Basics",
                "url": "https://example.com/ai-basics",
                "content": "Introduction to artificial intelligence concepts",
            },
            {
                "title": "Machine Learning Fundamentals",
                "url": "https://example.com/ml-fundamentals",
                "content": "Core concepts of machine learning and neural networks",
            },
        ]
    }
    mock_server.client.search.return_value = mock_search_response

    search_args = {
        "query": "artificial intelligence basics",
        "pageno": 1,
        "safesearch": 0,
    }

    result = await mock_server._handle_web_search(search_args)

    assert result is not None
    assert len(result) > 0
    assert "AI Basics" in result[0].text
    assert "https://example.com/ai-basics" in result[0].text
    mock_server.client.search.assert_called_once_with(
        query="artificial intelligence basics",
        pageno=1,
        time_range=None,
        language=None,
        safesearch=0,
    )


@pytest.mark.asyncio
async def test_fetch_functionality(mock_server: SearXNGServer) -> None:
    """Test URL fetch functionality"""
    mock_html_content = (
        "<html><body><h1>Test Page</h1><p>Test content</p></body></html>"
    )
    mock_server.client.fetch_url.return_value = mock_html_content

    fetch_args = {"url": "https://example.com/test"}
    result = await mock_server._handle_web_url_read(fetch_args)

    assert result is not None
    assert len(result) > 0
    assert "Test Page" in result[0].text
    assert "Test content" in result[0].text
    mock_server.client.fetch_url.assert_called_once_with("https://example.com/test")


async def demonstrate_search_and_fetch() -> None:
    """Demonstrate search and fetch functionality"""

    if not os.getenv("SEARXNG_URL"):
        print("Please set SEARXNG_URL environment variable")
        return

    server = SearXNGServer()

    print("🔍 Searching for 'artificial intelligence basics'...")
    search_args = {
        "query": "artificial intelligence basics",
        "pageno": 1,
        "safesearch": 0,
    }

    try:
        # Perform search
        search_results = await server._handle_web_search(search_args)

        if search_results and len(search_results) > 0:
            content = search_results[0].text
            print("✅ Search completed!\n")
            print(content[:500] + "..." if len(content) > 500 else content)

            # Extract first URL
            lines = content.split("\n")
            for line in lines:
                if line.startswith("URL: "):
                    url = line.replace("URL: ", "").strip()
                    print(f"\n🌐 Fetching content from: {url}")

                    try:
                        fetch_args = {"url": url}
                        fetch_result = await server._handle_web_url_read(fetch_args)

                        if fetch_result and len(fetch_result) > 0:
                            fetched_content = fetch_result[0].text
                            print(
                                f"✅ Successfully fetched {len(fetched_content)} characters"
                            )
                            print("📝 First 200 characters:")
                            print("-" * 40)
                            print(
                                fetched_content[:200] + "..."
                                if len(fetched_content) > 200
                                else fetched_content
                            )
                            print("-" * 40)
                        else:
                            print("❌ No content fetched")
                    except Exception as e:
                        print(f"❌ Error fetching URL: {e}")
                    break
        else:
            print("❌ No search results")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main() -> None:
    print("=== SearXNG Search MCP Server Example ===\n")
    await demonstrate_search_and_fetch()
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
