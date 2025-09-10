"""
SearXNG Search MCP Server

A Python implementation of SearXNG MCP (Model Context Protocol) server for web search
and URL fetching capabilities. This package enables AI models to perform web searches
through SearXNG search engine integration and retrieve web content in various formats.

Architecture:
    - Modular design with separate client, server, and entry point modules
    - HTTP client for SearXNG communication (client.py)
    - Main MCP server implementation (server_main.py)
    - Entry point with stdio transport (server.py)
    - Console script entry point (__main__.py)

Key Features:
    - Web search via SearXNG with configurable parameters
    - URL content fetching in multiple formats (markdown, html, text, json)
    - Authentication support (basic auth)
    - Proxy configuration support
    - Comprehensive error handling and logging
    - MCP protocol compliance

Environment Variables:
    - SEARXNG_URL: Base URL of the SearXNG instance (required)
    - AUTH_USERNAME: Username for basic authentication (optional)
    - AUTH_PASSWORD: Password for basic authentication (optional)
    - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR) (optional)

Usage:
    As MCP server:
    ```bash
    python -m searxng_search_mcp.server
    ```

    As console script:
    ```bash
    searxng-search-mcp
    ```

    Programmatic usage:
    ```python
    from searxng_search_mcp import SearXNGServer, SearXNGClient

    # Create client for direct API access
    client = SearXNGClient("https://searx.example.com")
    results = await client.search("query")

    # Create MCP server
    server = SearXNGServer()
    ```

Version: 0.1.0
"""

__version__ = "0.1.0"

from searxng_search_mcp.client import SearXNGClient
from searxng_search_mcp.server_main import SearXNGServer

__all__ = ["SearXNGServer", "SearXNGClient"]
