"""
SearXNG Search MCP Server

This module provides the main entry point for the SearXNG MCP (Model Context Protocol) server.
The server enables web search and content fetching capabilities through SearXNG search engine
integration, allowing AI models to perform web searches and retrieve web content.

Environment Variables:
    - SEARXNG_URL: Base URL of the SearXNG instance (required)
    - AUTH_USERNAME: Username for basic authentication (optional)
    - AUTH_PASSWORD: Password for basic authentication (optional)
    - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

Usage:
    This server is typically run as an MCP server through stdio transport:
    ```bash
    python -m searxng_search_mcp.server
    ```

    Or using the installed script:
    ```bash
    searxng-search-mcp
    ```
"""

import asyncio
import logging
import sys

import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from searxng_search_mcp.server_main import SearXNGServer
from searxng_search_mcp.utils import setup_logging, validate_environment

setup_logging("LOG_LEVEL", "INFO")
logger = logging.getLogger(__name__)


async def main_async() -> None:
    """
    Main asynchronous entry point for the SearXNG MCP server.

    This function initializes the server, sets up the stdio transport,
    and starts the MCP server with proper initialization options.

    Raises:
        ValueError: If required environment variables are not configured.
        RuntimeError: If server initialization fails.
    """
    try:
        validate_environment()
        logger.debug("Initializing SearXNG MCP server...")

        server = SearXNGServer()
        logger.debug(f"Server initialized successfully. Version: {server.VERSION}")

        logger.debug("Starting stdio transport...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.debug("MCP server running via stdio transport")
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="searxng-search-mcp",
                    server_version=server.VERSION,
                    capabilities=server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during server startup: {e}")
        sys.exit(1)


def main() -> None:
    """
    Synchronous entry point for the SearXNG MCP server.

    This function provides a synchronous wrapper around main_async() for
    compatibility with various execution environments and script runners.
    """
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
