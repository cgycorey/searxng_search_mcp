"""
Shared utilities for SearXNG Search MCP Server

This module provides common utilities used across the SearXNG MCP server
to avoid code duplication and ensure consistency.

Environment Variables Used:
    - SEARXNG_URL: Base URL of the SearXNG instance (required)
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR) (optional)

Functions:
    - validate_environment: Validate required environment variables and configuration
"""

import logging
import os
import sys


def validate_environment() -> None:
    """
    Validate required environment variables and configuration.

    This function checks for the presence and validity of required environment
    variables used by the SearXNG MCP server. It provides detailed error messages
    for missing or invalid configuration.

    Raises:
        ValueError: If required environment variables are missing or invalid.

    Example:
        ```python
        try:
            validate_environment()
            print("Environment validation passed")
        except ValueError as e:
            print(f"Configuration error: {e}")
        ```
    """
    required_vars = ["SEARXNG_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please set SEARXNG_URL to your SearXNG instance URL."
        )
        raise ValueError(error_msg)

    _validate_searxng_url_format()


def validate_environment_with_exit() -> None:
    """
    Validate required environment variables and exit on failure.

    This function is designed for use in console scripts and entry points where
    immediate exit is preferred over exception handling. It provides user-friendly
    error messages to stderr.

    Raises:
        SystemExit: Always exits with code 1 on validation failure.

    Example:
        ```python
        # In a console script
        validate_environment_with_exit()
        # If we reach here, environment is valid
        ```
    """
    required_vars = ["SEARXNG_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger = logging.getLogger(__name__)
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        print("Error: SEARXNG_URL environment variable is required", file=sys.stderr)
        print(
            "Example: SEARXNG_URL=https://searx.example.com uvx run searxng-search-mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        _validate_searxng_url_format()
    except ValueError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Invalid SEARXNG_URL format: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _validate_searxng_url_format() -> None:
    """
    Validate the format of SEARXNG_URL.

    Raises:
        ValueError: If SEARXNG_URL format is invalid.
    """
    searxng_url = os.getenv("SEARXNG_URL", "").strip()

    if not searxng_url.startswith(("http://", "https://")):
        raise ValueError(
            f"SEARXNG_URL must start with http:// or https://, got: {searxng_url}"
        )

    # Additional validation for URL format
    if not searxng_url.replace("http://", "").replace("https://", "").strip():
        raise ValueError("SEARXNG_URL cannot be empty")

    logger = logging.getLogger(__name__)
    logger.debug(f"Environment validation passed. SearXNG URL: {searxng_url}")


def setup_logging(
    log_level_env: str = "LOG_LEVEL", default_level: str = "INFO"
) -> None:
    """
    Set up logging configuration for the SearXNG MCP server.

    Args:
        log_level_env: Environment variable name for log level (default: "LOG_LEVEL")
        default_level: Default log level if environment variable is not set (default: "INFO")

    Example:
        ```python
        setup_logging("LOG_LEVEL", "DEBUG")
        # This will use DEBUG level if LOG_LEVEL is not set
        ```
    """
    log_level = os.getenv(log_level_env, default_level).upper()
    level = getattr(logging, log_level, getattr(logging, default_level))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def setup_logging_stderr(
    log_level_env: str = "LOG_LEVEL", default_level: str = "WARNING"
) -> None:
    """
    Set up logging configuration for the SearXNG MCP server with stderr output.

    This function is specifically designed for MCP compatibility where stderr
    is the preferred output stream for logs.

    Args:
        log_level_env: Environment variable name for log level (default: "LOG_LEVEL")
        default_level: Default log level if environment variable is not set (default: "WARNING")

    Example:
        ```python
        setup_logging_stderr("LOG_LEVEL", "INFO")
        # This will use INFO level if LOG_LEVEL is not set and output to stderr
        ```
    """
    log_level = os.getenv(log_level_env, default_level).upper()
    level = getattr(logging, log_level, getattr(logging, default_level))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

