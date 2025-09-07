"""
SearXNG Search MCP Server

A Python implementation of the SearXNG MCP server for web search and URL fetching.
"""

__version__ = "0.1.0"

from .server import SearXNGServer, SearXNGClient

__all__ = ["SearXNGServer", "SearXNGClient"]