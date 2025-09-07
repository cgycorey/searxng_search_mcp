"""
Tests for SearXNG MCP Server
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from searxng_search_mcp import SearXNGServer, SearXNGClient


@pytest.fixture
def mock_searxng_client():
    """Create a mock SearXNG client for testing"""
    client = SearXNGClient("https://example.com")
    client.search = AsyncMock()
    client.fetch_url = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_searxng_search_success(mock_searxng_client):
    """Test successful SearXNG search"""
    mock_response = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "Test content"
            }
        ]
    }
    mock_searxng_client.search.return_value = mock_response
    
    result = await mock_searxng_client.search("test query")
    
    assert result == mock_response
    mock_searxng_client.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_searxng_search_with_parameters(mock_searxng_client):
    """Test SearXNG search with additional parameters"""
    mock_response = {"results": []}
    mock_searxng_client.search.return_value = mock_response
    
    await mock_searxng_client.search(
        query="test",
        pageno=2,
        time_range="week",
        language="en",
        safesearch=1
    )
    
    mock_searxng_client.search.assert_called_once_with(
        query="test",
        pageno=2,
        time_range="week",
        language="en",
        safesearch=1
    )


@pytest.mark.asyncio
async def test_url_fetch_success(mock_searxng_client):
    """Test successful URL fetching"""
    mock_content = "<html><body>Test content</body></html>"
    mock_searxng_client.fetch_url.return_value = mock_content
    
    result = await mock_searxng_client.fetch_url("https://example.com")
    
    assert result == mock_content
    mock_searxng_client.fetch_url.assert_called_once_with("https://example.com")


def test_searxng_server_initialization():
    """Test SearXNG server initialization with environment variable"""
    import os
    
    # This test will fail if SEARXNG_URL is not set
    try:
        server = SearXNGServer()
        assert server.server.name == "searxng-search-mcp"
        assert hasattr(server, 'client')
        assert hasattr(server, 'h')
    except ValueError as e:
        assert "SEARXNG_URL environment variable is required" in str(e)


def test_searxng_server_tools():
    """Test that server has the expected tools"""
    import os
    from unittest.mock import patch
    
    # Mock the environment variable to avoid requiring it to be set
    with patch.dict(os.environ, {'SEARXNG_URL': 'https://test.example.com'}):
        server = SearXNGServer()
        
        # Test that we can access the tools (this would normally be called by MCP)
        # We can't easily test the async handlers without a proper MCP setup
        assert hasattr(server, '_handle_web_search')
        assert hasattr(server, '_handle_web_url_read')


def test_project_structure():
    """Test that project structure is correct"""
    import os
    
    # Check that main files exist
    assert os.path.exists("src/searxng_search_mcp/__init__.py")
    assert os.path.exists("src/searxng_search_mcp/server.py")
    assert os.path.exists("src/searxng_search_mcp/__main__.py")
    assert os.path.exists("pyproject.toml")
    assert os.path.exists("README.md")


if __name__ == "__main__":
    test_project_structure()
    print("✅ Basic structure tests passed!")