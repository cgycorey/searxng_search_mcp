#!/usr/bin/env python3
"""
Command-line entry point for SearXNG Search MCP Server

This module provides the console script entry point for the SearXNG MCP server.
It handles environment validation, logging configuration, and provides a user-friendly
interface for running the server from the command line.

Environment Variables:
    - SEARXNG_URL: Base URL of the SearXNG instance (required)
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR) (default: WARNING)
    - AUTH_USERNAME: Username for basic authentication (optional)
    - AUTH_PASSWORD: Password for basic authentication (optional)
    - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

Usage:
    Direct execution:
    ```bash
    python -m searxng_search_mcp
    ```

    Via installed script:
    ```bash
    searxng-search-mcp
    ```

    With environment variables:
    ```bash
    export SEARXNG_URL="https://searx.example.com"
    export LOG_LEVEL="INFO"
    searxng-search-mcp
    ```

Example:
    # Set required environment variable and run
    export SEARXNG_URL="https://searx.be"
    searxng-search-mcp
"""

import asyncio
import logging
import os
import sys

from searxng_search_mcp.server import main_async

# Configure logging to stderr for MCP compatibility
# Log level can be configured via LOG_LEVEL environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],  # Explicitly use stderr for MCP
)
logger = logging.getLogger(__name__)


def _validate_environment() -> None:
    """
    Validate required environment variables for console script execution.

    Raises:
        SystemExit: If required environment variables are missing or invalid.
    """
    required_vars = ["SEARXNG_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        print("Error: SEARXNG_URL environment variable is required", file=sys.stderr)
        print(
            "Example: SEARXNG_URL=https://searx.example.com uvx run searxng-search-mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate SEARXNG_URL format
    searxng_url = os.getenv("SEARXNG_URL", "").strip()
    if not searxng_url.startswith(("http://", "https://")):
        logger.error(f"Invalid SEARXNG_URL format: {searxng_url}")
        print(
            f"Error: SEARXNG_URL must start with http:// or https://, got: {searxng_url}",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.debug(f"Environment validation passed. SearXNG URL: {searxng_url}")


def main() -> None:
    """
    Entry point for console scripts.

    This function serves as the main entry point when the package is installed
    and run via the 'searxng-search-mcp' console script. It performs environment
    validation, sets up logging, and starts the MCP server.

    The function handles common startup errors gracefully and provides
    user-friendly error messages.

    Raises:
        SystemExit: With appropriate exit codes for different error conditions.
    """
    try:
        # Validate environment before starting
        _validate_environment()

        logger.debug("Starting SearXNG MCP server from console script...")
        return asyncio.run(main_async())

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        print("\nShutting down SearXNG MCP server...", file=sys.stderr)
        sys.exit(0)

    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise

    except Exception as e:
        logger.error(f"Fatal error in console script: {e}")
        print(f"Error running SearXNG MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
