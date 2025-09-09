"""
SearXNG Search MCP Server

A Python implementation of SearXNG MCP server for web search and URL fetching.
"""

__version__ = "0.1.0"

from searxng_search_mcp.client import SearXNGClient
from searxng_search_mcp.server_main import SearXNGServer

__all__ = ["SearXNGServer", "SearXNGClient"]
