# SearXNG Server Module
# Main MCP server implementation

"""
SearXNG Server Module

This module contains the main MCP (Model Context Protocol) server implementation
for SearXNG search functionality. It provides the core server logic, tool definitions,
and request handling for web search and URL content fetching capabilities.

Key Features:
    - MCP server implementation with stdio transport
    - Web search tool with configurable parameters
    - URL content fetching with multiple output formats
    - Comprehensive error handling and logging
    - Tool registration and capability management
    - HTML cleaning and content processing

Architecture:
    - SearXNGServer: Main server class implementing MCP protocol
    - Tool handlers for search and content fetching
    - HTML processing utilities
    - Environment configuration management

MCP Tools Provided:
    - metasearch_web: Search the web using SearXNG
    - fetch_web_content: Fetch and process web page content

Environment Variables:
    - SEARXNG_URL: Base URL of the SearXNG instance (required)
    - AUTH_USERNAME: Username for basic authentication (optional)
    - AUTH_PASSWORD: Password for basic authentication (optional)
    - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

Dependencies:
    - mcp: Model Context Protocol framework
    - httpx: HTTP client library
    - html2text: HTML to Markdown converter
    - beautifulsoup4: HTML parsing and cleaning
    - searxng_search_mcp.client: SearXNG HTTP client

Usage:
    This server is typically instantiated and run by the server.py entry point:

    ```python
    server = SearXNGServer()
    await server.server.run(read_stream, write_stream, initialization_options)
    ```
"""

import json
import logging
import os

import html2text
import httpx
import mcp.types as types
from bs4 import BeautifulSoup
from mcp.server import Server

from searxng_search_mcp.analyzer import SearchResultAnalyzer
from searxng_search_mcp.client import SearXNGClient

logger = logging.getLogger(__name__)


class SearXNGServer:
    """
    MCP server for SearXNG search functionality.

    This class implements the main MCP (Model Context Protocol) server that provides
    web search and URL content fetching capabilities through SearXNG integration.
    It handles tool registration, request processing, and response formatting.

    Attributes:
        VERSION (str): Server version string
        SUPPORTED_FORMATS (list): List of supported output formats for content fetching
        server (Server): MCP server instance
        client (SearXNGClient): HTTP client for SearXNG communication
        h (HTML2Text): HTML to Markdown converter instance

    Environment Variables:
        - SEARXNG_URL: Base URL of the SearXNG instance (required)
        - AUTH_USERNAME: Username for basic authentication (optional)
        - AUTH_PASSWORD: Password for basic authentication (optional)
        - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

    MCP Tools Provided:
        - metasearch_web: Search the web using SearXNG with various parameters
        - fetch_web_content: Fetch and process web page content in multiple formats

    Example:
        ```python
        # Create server instance
        server = SearXNGServer()

        # Server will automatically register tools and handle MCP protocol
        # The server is typically run via stdio transport:
        # await server.server.run(read_stream, write_stream, initialization_options)
        ```

    Architecture:
        - Uses MCP Server class for protocol handling
        - Integrates with SearXNGClient for HTTP communication
        - Provides HTML cleaning and content processing utilities
        - Implements comprehensive error handling and logging
        - Supports multiple output formats (markdown, html, text, json)

    Note:
        This server is designed to be used with stdio transport and is typically
        instantiated and managed by the server.py entry point module.
    """

    VERSION = "0.1.0"
    SUPPORTED_FORMATS = ["markdown", "html", "text", "json"]

    def __init__(self) -> None:
        """Initialize the SearXNG MCP server."""
        self.server = Server("searxng-search-mcp")
        self.client = self._create_client()
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.analyzer = SearchResultAnalyzer()

        self._setup_handlers()

        # Set content size limit
        max_content_size_env = os.getenv("SEARXNG_MAX_CONTENT_SIZE")
        self.MAX_CONTENT_SIZE = (
            int(max_content_size_env) if max_content_size_env else 10485760
        )

    def _create_client(self) -> SearXNGClient:
        """Create and configure the SearXNG client.

        Reads configuration from environment variables:
        - SEARXNG_URL: Base URL of the SearXNG instance (required)
        - AUTH_USERNAME: Username for basic authentication (optional)
        - AUTH_PASSWORD: Password for basic authentication (optional)
        - HTTP_PROXY/HTTPS_PROXY: Proxy configuration (optional)

        Returns:
            Configured SearXNGClient instance

        Raises:
            ValueError: If SEARXNG_URL is not set
        """
        base_url = os.getenv("SEARXNG_URL")
        if not base_url:
            logger.error("SEARXNG_URL environment variable is required")
            raise ValueError("SEARXNG_URL environment variable is required")

        auth = None
        username = os.getenv("AUTH_USERNAME")
        password = os.getenv("AUTH_PASSWORD")
        if username and password:
            auth = (username, password)

        proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        if proxy:
            logger.debug(f"Using proxy: {proxy}")

        return SearXNGClient(base_url, auth, proxy)

    def _setup_handlers(self) -> None:
        @self.server.list_tools()  # type: ignore[misc]
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="metasearch_web",
                    description=(
                        "Search the web using SearXNG. After getting search results, "
                        "you can fetch full content from any URL using the fetch_web_content tool."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "pageno": {
                                "type": "integer",
                                "description": "Page number (default: 1)",
                                "default": 1,
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range filter (day, week, month, year)",
                                "enum": ["day", "week", "month", "year"],
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (e.g., en, de, fr)",
                            },
                            "safesearch": {
                                "type": "integer",
                                "description": "Safe search level (0: none, 1: moderate, 2: strict)",
                                "default": 0,
                                "minimum": 0,
                                "maximum": 2,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="fetch_web_content",
                    description=(
                        "Fetch full content from web page URLs (including URLs from search results). "
                        "Supports multiple formats: html, markdown, text, json."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"},
                            "format": {
                                "type": "string",
                                "description": "Output format",
                                "enum": ["markdown", "html", "text", "json"],
                                "default": "markdown",
                            },
                            "raw": {
                                "type": "boolean",
                                "description": "Return raw content without processing",
                                "default": False,
                            },
                        },
                        "required": ["url"],
                    },
                ),
                types.Tool(
                    name="analyze_search_results",
                    description=(
                        "Analyze search results to extract insights, patterns, and actionable information. "
                        "Provides multiple analysis types: summary, trends, sources, keywords, relevance."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_results": {
                                "type": "array",
                                "description": "Array of search result objects from metasearch_web",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "url": {"type": "string"},
                                        "content": {"type": "string"},
                                    },
                                },
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis to perform",
                                "enum": [
                                    "summary",
                                    "trends",
                                    "sources",
                                    "keywords",
                                    "relevance",
                                ],
                                "default": "summary",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to analyze (default: 10)",
                                "default": 10,
                            },
                        },
                        "required": ["search_results"],
                    },
                ),
            ]

        @self.server.call_tool()  # type: ignore[misc]
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}

            if name == "metasearch_web":
                return await self._handle_web_search(arguments)
            elif name == "fetch_web_content":
                return await self._handle_web_url_read(arguments)
            elif name == "analyze_search_results":
                return await self._handle_analyze_search_results(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_web_search(self, arguments: dict) -> list[types.TextContent]:
        query = arguments.get("query", "")
        pageno = arguments.get("pageno", 1)
        time_range = arguments.get("time_range")
        language = arguments.get("language")
        safesearch = arguments.get("safesearch", 0)

        if not query.strip():
            logger.warning("Empty search query received")
            return [types.TextContent(type="text", text="Search query is required")]

        try:
            logger.debug(f"Executing web search for query: {query[:100]}...")
            results = await self.client.search(
                query=query,
                pageno=pageno,
                time_range=time_range,
                language=language,
                safesearch=safesearch,
            )

            search_results = results.get("results", [])
            if not search_results:
                logger.debug("No search results found")
                return [types.TextContent(type="text", text="No results found")]

            formatted_results = []
            for i, result in enumerate(search_results, 1):
                formatted_results.append(
                    f"**Result {i}: {result.get('title', 'No title')}**"
                )
                formatted_results.append(f"URL: {result.get('url', 'No URL')}")
                if result.get("content"):
                    # Clean up content - remove extra whitespace
                    content = result["content"].strip()
                    if content:
                        formatted_results.append(f"Content: {content}")
                formatted_results.append("")

            response_text = "\n".join(formatted_results)
            logger.debug(
                f"Returning {len(search_results)} "
                f"search result{'' if len(search_results) == 1 else 's'}"
            )
            return [types.TextContent(type="text", text=response_text)]

        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return [
                types.TextContent(type="text", text=f"Configuration error: {str(e)}")
            ]
        except httpx.TimeoutException:
            logger.error(f"Search timeout for query: {query[:100]}...")
            return [
                types.TextContent(
                    type="text", text="Search request timed out. Please try again."
                )
            ]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} during search")
            return [
                types.TextContent(
                    type="text",
                    text=f"Search failed with HTTP error {e.response.status_code}",
                )
            ]
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            return [
                types.TextContent(
                    type="text", text=f"Error performing search: {str(e)}"
                )
            ]

    def _clean_html(self, html_content: str) -> BeautifulSoup:
        """Clean HTML content by removing scripts and styles.

        Args:
            html_content: Raw HTML content

        Returns:
            BeautifulSoup object with cleaned HTML
        """
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        return soup

    async def _handle_web_url_read(self, arguments: dict) -> list[types.TextContent]:
        url = arguments.get("url", "")
        output_format = arguments.get("format", "markdown")
        raw = arguments.get("raw", False)

        if not url.strip():
            logger.warning("Empty URL received")
            return [types.TextContent(type="text", text="URL is required")]

        try:
            logger.debug(f"Fetching web content from: {url[:100]}...")
            html_content = await self.client.fetch_url(url)

            # Check content size limits
            if len(html_content) > self.MAX_CONTENT_SIZE:
                logger.warning(
                    f"Content size {len(html_content)} exceeds limit {self.MAX_CONTENT_SIZE}"
                )
                return [
                    types.TextContent(
                        type="text",
                        text=f"Content too large ({len(html_content)} bytes). "
                        f"Maximum allowed size is {self.MAX_CONTENT_SIZE} bytes.",
                    )
                ]

            if raw:
                # Return raw content
                content = html_content
                logger.debug(f"Returning raw content ({len(content)} characters)")
            elif output_format == "html":
                # Return cleaned HTML
                soup = self._clean_html(html_content)
                content = str(soup)
                logger.debug(
                    f"Returning cleaned HTML content ({len(content)} characters)"
                )
            elif output_format == "text":
                # Return plain text
                soup = self._clean_html(html_content)
                content = soup.get_text(separator=" ", strip=True)
                logger.debug(
                    f"Returning plain text content ({len(content)} characters)"
                )
            elif output_format == "json":
                # Return structured JSON
                soup = self._clean_html(html_content)

                structured_data = {
                    "url": url,
                    "title": soup.title.string if soup.title else None,
                    "content": soup.get_text(separator=" ", strip=True),
                    "html": str(soup),
                    "markdown": self.h.handle(str(soup)),
                    "metadata": {"length": len(html_content), "format": "json"},
                }
                content = json.dumps(structured_data, indent=2, ensure_ascii=False)
                logger.debug(f"Returning JSON content ({len(content)} characters)")
            else:  # markdown (default)
                # Return markdown
                soup = self._clean_html(html_content)
                content = self.h.handle(str(soup))
                logger.debug(f"Returning markdown content ({len(content)} characters)")

            return [types.TextContent(type="text", text=content)]

        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return [
                types.TextContent(type="text", text=f"Configuration error: {str(e)}")
            ]
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching URL: {url[:100]}...")
            return [
                types.TextContent(
                    type="text", text="Request timed out. Please try again."
                )
            ]
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} fetching URL: {url[:100]}..."
            )
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to fetch URL: HTTP error {e.response.status_code}",
                )
            ]
        except Exception as e:
            logger.error(f"Unexpected error fetching URL {url[:100]}...: {str(e)}")
            return [
                types.TextContent(type="text", text=f"Error fetching URL: {str(e)}")
            ]

    async def _handle_analyze_search_results(
        self, arguments: dict
    ) -> list[types.TextContent]:
        """Handle search result analysis requests."""
        search_results = arguments.get("search_results", [])
        analysis_type = arguments.get("analysis_type", "summary")
        max_results = arguments.get("max_results", 10)

        if not search_results:
            logger.warning("Empty search results received for analysis")
            return [
                types.TextContent(
                    type="text", text="Search results are required for analysis"
                )
            ]

        try:
            logger.debug(
                f"Analyzing {len(search_results)} search results with type: {analysis_type}"
            )

            # Configure analyzer with max results
            self.analyzer.max_results = max_results

            # Perform analysis
            analysis_results = self.analyzer.analyze_search_results(
                search_results=search_results, analysis_type=analysis_type
            )

            # Format results as JSON
            response_text = json.dumps(analysis_results, indent=2, ensure_ascii=False)
            logger.debug(
                f"Analysis completed successfully. Results length: {len(response_text)} characters"
            )

            return [types.TextContent(type="text", text=response_text)]

        except ValueError as e:
            logger.error(f"Analysis configuration error: {str(e)}")
            return [
                types.TextContent(
                    type="text", text=f"Analysis configuration error: {str(e)}"
                )
            ]
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            return [
                types.TextContent(
                    type="text", text=f"Error performing analysis: {str(e)}"
                )
            ]
