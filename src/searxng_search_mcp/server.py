import os
from typing import Any, Dict, Optional
import httpx
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from bs4 import BeautifulSoup
import html2text


class SearXNGClient:
    def __init__(self, base_url: str, auth: Optional[tuple] = None, proxy: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.proxy = proxy
        
    async def search(self, query: str, pageno: int = 1, time_range: Optional[str] = None, 
                    language: Optional[str] = None, safesearch: int = 0) -> Dict[str, Any]:
        params = {
            'q': query,
            'pageno': pageno,
            'safesearch': safesearch,
            'format': 'json'
        }
        
        if time_range:
            params['time_range'] = time_range
        if language:
            params['language'] = language
            
        async with httpx.AsyncClient(
            auth=self.auth,
            proxy=self.proxy,
            timeout=120.0
        ) as client:
            response = await client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            return response.json()
    
    async def fetch_url(self, url: str) -> str:
        async with httpx.AsyncClient(
            auth=self.auth,
            proxy=self.proxy,
            timeout=120.0
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text


class SearXNGServer:
    def __init__(self):
        self.server = Server("searxng-search-mcp")
        self.client = self._create_client()
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        
        self._setup_handlers()
    
    def _create_client(self) -> SearXNGClient:
        base_url = os.getenv('SEARXNG_URL')
        if not base_url:
            raise ValueError("SEARXNG_URL environment variable is required")
            
        auth = None
        username = os.getenv('AUTH_USERNAME')
        password = os.getenv('AUTH_PASSWORD')
        if username and password:
            auth = (username, password)
            
        proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
        
        return SearXNGClient(base_url, auth, proxy)
    
    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="metasearch_web",
                    description="Search the web using SearXNG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "pageno": {
                                "type": "integer",
                                "description": "Page number (default: 1)",
                                "default": 1
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Time range filter (day, week, month, year)",
                                "enum": ["day", "week", "month", "year"]
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (e.g., en, de, fr)"
                            },
                            "safesearch": {
                                "type": "integer",
                                "description": "Safe search level (0: none, 1: moderate, 2: strict)",
                                "default": 0,
                                "minimum": 0,
                                "maximum": 2
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="fetch_web_content",
                    description="Fetch web page content in multiple formats (html, markdown, text, json)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format",
                                "enum": ["markdown", "html", "text", "json"],
                                "default": "markdown"
                            },
                            "raw": {
                                "type": "boolean",
                                "description": "Return raw content without processing",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[dict]) -> list[types.TextContent]:
            if arguments is None:
                arguments = {}
                
            if name == "metasearch_web":
                return await self._handle_web_search(arguments)
            elif name == "fetch_web_content":
                return await self._handle_web_url_read(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_web_search(self, arguments: dict) -> list[types.TextContent]:
        query = arguments.get("query", "")
        pageno = arguments.get("pageno", 1)
        time_range = arguments.get("time_range")
        language = arguments.get("language")
        safesearch = arguments.get("safesearch", 0)
        
        try:
            results = await self.client.search(
                query=query,
                pageno=pageno,
                time_range=time_range,
                language=language,
                safesearch=safesearch
            )
            
            formatted_results = []
            for result in results.get('results', []):
                formatted_results.append(f"**{result.get('title', 'No title')}**")
                formatted_results.append(f"URL: {result.get('url', 'No URL')}")
                if result.get('content'):
                    formatted_results.append(f"Content: {result['content']}")
                formatted_results.append("")
            
            return [types.TextContent(
                type="text",
                text="\n".join(formatted_results) if formatted_results else "No results found"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error performing search: {str(e)}"
            )]
    
    async def _handle_web_url_read(self, arguments: dict) -> list[types.TextContent]:
        url = arguments.get("url", "")
        output_format = arguments.get("format", "markdown")
        raw = arguments.get("raw", False)
        
        if not url:
            return [types.TextContent(
                type="text",
                text="URL is required"
            )]
        
        try:
            html_content = await self.client.fetch_url(url)
            
            if raw:
                # Return raw content
                content = html_content
            elif output_format == "html":
                # Return cleaned HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                content = str(soup)
            elif output_format == "text":
                # Return plain text
                soup = BeautifulSoup(html_content, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                content = soup.get_text(separator=' ', strip=True)
            elif output_format == "json":
                # Return structured JSON
                soup = BeautifulSoup(html_content, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                
                import json
                structured_data = {
                    "url": url,
                    "title": soup.title.string if soup.title else None,
                    "content": soup.get_text(separator=' ', strip=True),
                    "html": str(soup),
                    "markdown": self.h.handle(str(soup)),
                    "metadata": {
                        "length": len(html_content),
                        "format": "json"
                    }
                }
                content = json.dumps(structured_data, indent=2, ensure_ascii=False)
            else:  # markdown (default)
                # Return markdown
                soup = BeautifulSoup(html_content, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                content = self.h.handle(str(soup))
            
            return [types.TextContent(
                type="text",
                text=content
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error fetching URL: {str(e)}"
            )]


async def main_async():
    server = SearXNGServer()
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="searxng-search-mcp",
                server_version="0.1.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


