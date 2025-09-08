"""
SearXNG Search MCP Server

A Python implementation of the SearXNG MCP server for web search and URL fetching.
"""

__version__ = "0.1.0"

from .server import SearXNGClient, SearXNGServer

__all__ = ["SearXNGServer", "SearXNGClient"]
