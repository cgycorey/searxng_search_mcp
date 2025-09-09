# SearXNG Client Module
# Handles HTTP communication with SearXNG search engine

import logging
from typing import Any, Dict, Mapping, Optional, cast

import httpx

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Client for interacting with SearXNG search engine."""

    DEFAULT_TIMEOUT = 120.0
    MAX_LOG_LENGTH = 100

    def __init__(
        self, base_url: str, auth: Optional[tuple] = None, proxy: Optional[str] = None
    ):
        """Initialize the SearXNG client.

        Args:
            base_url: The base URL of the SearXNG instance
            auth: Optional authentication tuple (username, password)
            proxy: Optional proxy URL
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.proxy = proxy

    async def search(
        self,
        query: str,
        pageno: int = 1,
        time_range: Optional[str] = None,
        language: Optional[str] = None,
        safesearch: int = 0,
    ) -> Dict[str, Any]:
        """Perform a search query against SearXNG.

        Args:
            query: Search query string
            pageno: Page number for results pagination
            time_range: Time range filter (day, week, month, year)
            language: Language code for results
            safesearch: Safe search level (0: none, 1: moderate, 2: strict)

        Returns:
            Dictionary containing search results
        """
        logger.info(f"Performing search query: {query[:self.MAX_LOG_LENGTH]}...")

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
                auth=self.auth, proxy=self.proxy, timeout=self.DEFAULT_TIMEOUT
            ) as client:
                response = await client.get(
                    f"{self.base_url}/search", params=cast(Mapping[str, Any], params)
                )
                response.raise_for_status()
                result = cast(Dict[str, Any], response.json())
                results_count = len(result.get("results", []))
                logger.info(
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
        """Fetch content from a URL.

        Args:
            url: The URL to fetch content from

        Returns:
            The HTML content as a string
        """
        logger.info(f"Fetching content from URL: {url[:self.MAX_LOG_LENGTH]}...")

        try:
            async with httpx.AsyncClient(
                auth=self.auth, proxy=self.proxy, timeout=self.DEFAULT_TIMEOUT
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text
                logger.info(
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
