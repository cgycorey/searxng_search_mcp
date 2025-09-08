#!/usr/bin/env python3
"""
Command-line entry point for SearXNG Search MCP Server
"""

import asyncio
import logging
import os
import sys

from searxng_search_mcp.server import main_async

# Configure logging to stderr for MCP compatibility
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format="%(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],  # Explicitly use stderr
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Entry point for console scripts"""
    # Check if SEARXNG_URL is set
    if not os.getenv("SEARXNG_URL"):
        logger.error("SEARXNG_URL environment variable is required")
        print("Error: SEARXNG_URL environment variable is required", file=sys.stderr)
        print(
            "Example: SEARXNG_URL=https://searx.example.com uvx run searxng-search-mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
