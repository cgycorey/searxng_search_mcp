"""
SearXNG Search MCP Server

This module provides the main entry point for the SearXNG MCP (Model Context Protocol) server.
The server enables web search and content fetching capabilities through SearXNG search engine
integration, allowing AI models to perform web searches and retrieve web content.

Architecture:
    - This server module acts as the entry point and initializes the MCP server
    - The main SearXNGServer implementation is in server_main.py
    - Uses stdio transport for MCP communication
    - Configures logging and initializes the server with proper capabilities

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

Example:
    # Set required environment variable
    export SEARXNG_URL="https://searx.example.com"

    # Run the server
    python -m searxng_search_mcp.server
"""

import asyncio
import logging
import os
import sys

import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from searxng_search_mcp.server_main import SearXNGServer

# Configure logging to stderr for MCP compatibility
# Log level can be configured via LOG_LEVEL environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def _validate_environment() -> None:
    """
    Validate required environment variables and configuration.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    required_vars = ["SEARXNG_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please set SEARXNG_URL to your SearXNG instance URL."
        )

    # Validate SEARXNG_URL format
    searxng_url = os.getenv("SEARXNG_URL", "").strip()
    if not searxng_url.startswith(("http://", "https://")):
        raise ValueError(
            f"SEARXNG_URL must start with http:// or https://, got: {searxng_url}"
        )

    logger.debug(f"Environment validation passed. SearXNG URL: {searxng_url}")


async def main_async() -> None:
    """
    Main asynchronous entry point for the SearXNG MCP server.

    This function initializes the server, sets up the stdio transport,
    and starts the MCP server with proper initialization options.

    The server will run until interrupted or until the stdio streams are closed.

    Raises:
        ValueError: If required environment variables are not configured.
        RuntimeError: If server initialization fails.
    """
    try:
        # Validate environment before starting
        _validate_environment()

        logger.debug("Initializing SearXNG MCP server...")

        # Create the main server instance
        server = SearXNGServer()
        logger.debug(f"Server initialized successfully. Version: {server.VERSION}")

        # Set up stdio transport and run the server
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

    Usage:
        This function is intended to be used as the main entry point when
        the module is run directly or via the installed script.
    """
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
