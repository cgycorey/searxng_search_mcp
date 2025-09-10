# SearXNG Client Module
# Handles HTTP communication with SearXNG search engine

"""
SearXNG Client Module

This module provides the HTTP client for communicating with SearXNG search engine instances.
It handles search queries, URL fetching, authentication, and proxy configuration.

Key Features:
    - Asynchronous HTTP client using httpx
    - Search query execution with configurable parameters
    - URL content fetching with timeout handling
    - Basic authentication support
    - Proxy configuration support
    - Comprehensive error handling and logging
    - Configurable timeouts and logging limits

Environment Variables Used:
    - SEARXNG_URL: Base URL of the SearXNG instance (set in server_main.py)
    - AUTH_USERNAME: Username for basic authentication (optional)
    - AUTH_PASSWORD: Password for basic authentication (optional)
    - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

Typical Usage:
    This client is typically instantiated and used by the SearXNGServer class:

    ```python
    client = SearXNGClient("https://searx.example.com", auth=(user, pass))
    results = await client.search("query", pageno=1, time_range="week")
    content = await client.fetch_url("https://example.com")
    ```

Error Handling:
    - TimeoutException: When requests exceed the timeout limit
    - HTTPStatusError: For HTTP error responses
    - ValueError: For configuration errors
    - Generic Exception: For unexpected errors
"""

import logging
import os
import re
from typing import Any, Dict, Mapping, Optional, cast
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class SearXNGClient:
    """
    Client for interacting with SearXNG search engine.

    This class provides an asynchronous HTTP client for communicating with
    SearXNG instances. It handles search queries, URL content fetching,
    authentication, and proxy configuration.

    Attributes:
        base_url (str): The base URL of the SearXNG instance (stripped of trailing slashes)
        auth (Optional[tuple]): Authentication tuple (username, password) if configured
        proxy (Optional[str]): Proxy URL if configured
        DEFAULT_TIMEOUT (float): Default timeout for HTTP requests (120 seconds)
        MAX_LOG_LENGTH (int): Maximum length for logged URLs and queries (100 characters)

    Environment Variables:
        - SEARXNG_URL: Base URL of the SearXNG instance (required, passed via constructor)
        - AUTH_USERNAME: Username for basic authentication (optional)
        - AUTH_PASSWORD: Password for basic authentication (optional)
        - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

    Example:
        ```python
        # Basic usage
        client = SearXNGClient("https://searx.example.com")
        results = await client.search("python programming")

        # With authentication
        client = SearXNGClient("https://searx.example.com", auth=("user", "pass"))

        # With proxy
        client = SearXNGClient("https://searx.example.com", proxy="http://proxy:8080")
        ```

    Note:
        This client is designed to be used within an async context.
        All methods are asynchronous and should be awaited.
    """

    DEFAULT_TIMEOUT = 120.0
    MAX_LOG_LENGTH = 100

    def __init__(
        self, base_url: str, auth: Optional[tuple] = None, proxy: Optional[str] = None
    ):
        """
        Initialize the SearXNG client.

        Args:
            base_url: The base URL of the SearXNG instance (e.g., "https://searx.example.com")
            auth: Optional authentication tuple (username, password) for basic auth
            proxy: Optional proxy URL for HTTP requests (e.g., "http://proxy:8080")

        Example:
            ```python
            # Basic client
            client = SearXNGClient("https://searx.be")

            # Client with authentication
            client = SearXNGClient(
                "https://searx.example.com",
                auth=("username", "password")
            )

            # Client with proxy
            client = SearXNGClient(
                "https://searx.example.com",
                proxy="http://proxy.example.com:8080"
            )
            ```

        Note:
            The base_url will be stripped of trailing slashes automatically.
            Authentication and proxy are optional and can be None.
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.proxy = proxy
        timeout_env = os.getenv("SEARXNG_TIMEOUT")
        self.timeout = float(timeout_env) if timeout_env else self.DEFAULT_TIMEOUT

        # Client initialization details logged at debug level only
        logger.debug(f"Initialized SearXNG client for: {self.base_url}")
        logger.debug(f"Timeout configured: {self.timeout}s")
        if auth:
            logger.debug("Authentication configured")
        if proxy:
            logger.debug(f"Proxy configured: {proxy}")

    async def search(
        self,
        query: str,
        pageno: int = 1,
        time_range: Optional[str] = None,
        language: Optional[str] = None,
        safesearch: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform a search query against SearXNG.

        This method sends a search request to the configured SearXNG instance
        and returns the results in JSON format. It supports various search
        parameters to refine the search results.

        Args:
            query: Search query string (required)
            pageno: Page number for results pagination (default: 1)
            time_range: Time range filter - "day", "week", "month", or "year" (optional)
            language: Language code for results (e.g., "en", "de", "fr") (optional)
            safesearch: Safe search level - 0 (none), 1 (moderate), 2 (strict) (default: 0)

        Returns:
            Dictionary containing search results with the following structure:
            ```python
            {
                "query": "search query",
                "number_of_results": 123,
                "results": [
                    {
                        "title": "Result title",
                        "url": "https://example.com",
                        "content": "Snippet content...",
                        "engine": "google",
                        # ... other engine-specific fields
                    },
                    # ... more results
                ],
                # ... other metadata
            }
            ```

        Raises:
            httpx.TimeoutException: If the search request times out
            httpx.HTTPStatusError: If the SearXNG server returns an HTTP error
            Exception: For unexpected errors during the search

        Example:
            ```python
            # Basic search
            results = await client.search("python programming")

            # Search with time filter
            results = await client.search(
                "python programming",
                time_range="week",
                language="en"
            )

            # Paginated search
            results = await client.search("python", pageno=2)
            ```

        Note:
            Search queries are truncated in logs to MAX_LOG_LENGTH (100 characters)
            for privacy and readability. The actual query sent to SearXNG is not truncated.
        """
        logger.debug(f"Performing search query: {query[:self.MAX_LOG_LENGTH]}...")

        params = {
            "q": query,
            "pageno": pageno,
            "safesearch": safesearch,
            "format": "json",
        }

        if time_range:
            params["time_range"] = time_range
        if language:
            params["language"] = language

        try:
            async with httpx.AsyncClient(
                auth=self.auth, proxy=self.proxy, timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}/search", params=cast(Mapping[str, Any], params)
                )
                response.raise_for_status()
                result = cast(Dict[str, Any], response.json())
                results_count = len(result.get("results", []))
                logger.debug(
                    f"Search completed successfully, found {results_count} "
                    f"result{'' if results_count == 1 else 's'}"
                )
                return result
        except httpx.TimeoutException:
            logger.error(f"Search timeout for query: {query[:self.MAX_LOG_LENGTH]}...")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} for search query: "
                f"{query[:self.MAX_LOG_LENGTH]}..."
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            raise

    async def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL.

        This method retrieves the HTML content from the specified URL using
        the same authentication and proxy configuration as the search client.
        It's commonly used to fetch full content of URLs found in search results.

        Args:
            url: The URL to fetch content from (must be a valid HTTP/HTTPS URL)

        Returns:
            The HTML content as a string. The content is returned as-is
            without any processing or cleaning.

        Raises:
            httpx.TimeoutException: If the request times out (configurable timeout)
            httpx.HTTPStatusError: If the server returns an HTTP error status
            ValueError: If the URL is invalid or potentially malicious
            Exception: For unexpected errors during the fetch operation

        Example:
            ```python
            # Fetch content from a URL
            html_content = await client.fetch_url("https://example.com")
            print(f"Fetched {len(html_content)} characters")

            # Fetch content from a search result URL
            search_results = await client.search("python tutorial")
            if search_results["results"]:
                first_url = search_results["results"][0]["url"]
                content = await client.fetch_url(first_url)
            ```

        Note:
            - Uses the same timeout, authentication, and proxy settings as search requests
            - URLs are truncated in logs to MAX_LOG_LENGTH (100 characters) for readability
            - The actual URL requested is not truncated
            - Content length is logged for monitoring purposes
            - This method fetches raw HTML - use server_main.py methods for processed content
            - Includes basic URL validation to prevent SSRF attacks
        """
        # Validate URL to prevent SSRF attacks
        if not self._is_safe_url(url):
            raise ValueError(
                f"Invalid or potentially malicious URL: {url[:self.MAX_LOG_LENGTH]}..."
            )

        logger.debug(f"Fetching content from URL: {url[:self.MAX_LOG_LENGTH]}...")

        try:
            async with httpx.AsyncClient(
                auth=self.auth, proxy=self.proxy, timeout=self.timeout
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text
                logger.debug(
                    f"Successfully fetched {len(content)} characters from "
                    f"{url[:self.MAX_LOG_LENGTH//2]}..."
                )
                return content
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching URL: {url[:self.MAX_LOG_LENGTH]}...")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} fetching URL: "
                f"{url[:self.MAX_LOG_LENGTH]}..."
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error fetching URL {url[:self.MAX_LOG_LENGTH]}...: "
                f"{str(e)}"
            )
            raise

    def _is_safe_url(self, url: str) -> bool:
        """
        Validate URL to prevent SSRF attacks and other security issues.

        Args:
            url: The URL to validate

        Returns:
            True if the URL is safe, False otherwise
        """
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ("http", "https"):
                return False

            # Check for private/reserved IP addresses in hostname
            hostname = parsed.hostname
            if hostname:
                # Check for localhost/private IPs
                if hostname in ("localhost", "127.0.0.1", "::1"):
                    return False

                # Check for private IP ranges
                import ipaddress

                try:
                    ip = ipaddress.ip_address(hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return False
                except ValueError:
                    # Not an IP address, continue with hostname validation
                    pass

                # Check for potentially dangerous hostnames
                dangerous_patterns = [
                    r"^192\.168\.",
                    r"^10\.",
                    r"^172\.(1[6-9]|2[0-9]|3[01])\.",
                    r"^127\.",
                    r"^169\.254\.",
                    r"^::1$",
                    r"^localhost$",
                ]

                for pattern in dangerous_patterns:
                    if re.match(pattern, hostname):
                        return False

            return True

        except Exception:
            return False
