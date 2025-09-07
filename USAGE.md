# Quick Start Guide

## Installation & Setup

### 1. Build the wheel
```bash
uv build
```

### 2. Set up environment variable
```bash
export SEARXNG_URL=https://searx.example.com
```

### 3. Run the server

**Option A: Development (from source)**
```bash
env SEARXNG_URL=https://searx.example.com uvx run searxng-search-mcp
```

**Option B: Production (from wheel)**
```bash
env SEARXNG_URL=https://searx.example.com uvx --from ./dist/searxng_search_mcp-0.1.0-py3-none-any.whl searxng-search-mcp
```

**Option C: Install as tool**
```bash
uv tool install ./dist/searxng_search_mcp-0.1.0-py3-none-any.whl
env SEARXNG_URL=https://searx.example.com searxng-search-mcp
```

## Available Tools

### 1. Web Search
Search the web using SearXNG
- **Tool name**: `metasearch_web`
- **Required**: `query` (search term)
- **Optional**: `pageno`, `time_range`, `language`, `safesearch`

### 2. URL Fetching
Fetch web page content in multiple formats
- **Tool name**: `fetch_web_content`
- **Required**: `url` (web page URL)
- **Optional**: `format` (markdown, html, text, json), `raw` (boolean)

## Example Usage

### Basic Search
```
Tool: metasearch_web
Parameters:
{
  "query": "python programming tutorial"
}
```

### Advanced Search
```
Tool: metasearch_web
Parameters:
{
  "query": "machine learning",
  "pageno": 1,
  "time_range": "month",
  "language": "en",
  "safesearch": 1
}
```

### Fetch Web Page
```
Tool: fetch_web_content
Parameters:
{
  "url": "https://example.com/article",
  "format": "markdown"
}
```

### Fetch in JSON Format
```
Tool: fetch_web_content
Parameters:
{
  "url": "https://example.com/article",
  "format": "json"
}
```

## Configuration Options

### Environment Variables
- `SEARXNG_URL`: Your SearXNG instance URL (required)
- `AUTH_USERNAME`: Username for protected instances (optional)
- `AUTH_PASSWORD`: Password for protected instances (optional)
- `HTTP_PROXY`: Proxy server URL (optional)
- `HTTPS_PROXY`: HTTPS proxy server URL (optional)

### Popular Public SearXNG Instances
- Find public instances at https://searx.space/
- Always check the privacy policy of any instance you use

## Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "searxng-search": {
      "command": "uvx",
      "args": ["--from", "/path/to/dist/searxng_search_mcp-0.1.0-py3-none-any.whl", "searxng-search-mcp"],
      "env": {
        "SEARXNG_URL": "https://your-searxng-instance.com"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues
1. **"SEARXNG_URL environment variable is required"**
   - Set the environment variable before running

2. **"coroutine was never awaited"**
   - Use the correct uvx syntax: `uvx --from wheel file`

3. **Connection timeouts**
   - Check your SearXNG instance is accessible
   - Consider using a different instance

### Testing
```bash
# Test the server starts correctly
timeout 5 env SEARXNG_URL=https://your-searxng-instance.com uvx --from ./dist/searxng_search_mcp-0.1.0-py3-none-any.whl searxng-search-mcp
```

## More Information
- Full documentation: README.md
- Repository: https://github.com/cgycorey/searxng_search_mcp
- Issues: https://github.com/cgycorey/searxng_search_mcp/issues