# SearXNG Search MCP Server Examples

This directory contains comprehensive examples demonstrating various use cases and scenarios for the SearXNG Search MCP Server.

## Available Examples

### 1. Basic Examples (`test_demo.py`)
- **Location**: `tests/test_demo.py`
- **Purpose**: Basic functionality demonstration and unit tests
- **Features**:
  - Mock-based testing for search and fetch operations
  - Live demonstration with real SearXNG instance
  - Error handling examples
  - Simple search and fetch workflow

### 2. Advanced Examples (`advanced_examples.py`)
- **Location**: `examples/advanced_examples.py`
- **Purpose**: Advanced features and use cases
- **Features**:
  - Basic web search
  - Filtered search (time range, language, safe search)
  - Multiple content formats (markdown, HTML, text, JSON)
  - Raw HTML content fetching
  - Complete search and fetch workflow
  - Error handling scenarios

### 3. Integration Examples (`integration_examples.py`)
- **Location**: `examples/integration_examples.py`
- **Purpose**: Real-world integration scenarios
- **Features**:
  - Research assistant workflow
  - News monitoring system
  - Content aggregation from multiple sources
  - Competitive analysis
  - Multi-topic processing

### 4. Performance Benchmarks (`performance_benchmarks.py`)
- **Location**: `examples/performance_benchmarks.py`
- **Purpose**: Performance testing and optimization
- **Features**:
  - Search performance benchmarking
  - Content fetch performance testing
  - Concurrent request handling
  - Stress testing
  - Memory usage analysis

## Running Examples

### Prerequisites

1. Set up your SearXNG instance URL:
```bash
export SEARXNG_URL=https://your-searxng-instance.com
```

2. Install dependencies:
```bash
uv sync --all-extras
```

### Running Individual Examples

```bash
# Basic examples (from tests directory)
cd tests
python test_demo.py

# Advanced examples
cd examples
python advanced_examples.py

# Integration examples
python integration_examples.py

# Performance benchmarks
python performance_benchmarks.py
```

### Running with Different Configurations

#### With Authentication
```bash
SEARXNG_URL=https://your-searxng-instance.com \
AUTH_USERNAME=your_username \
AUTH_PASSWORD=your_password \
python examples/advanced_examples.py
```

#### With Proxy
```bash
SEARXNG_URL=https://your-searxng-instance.com \
HTTP_PROXY=http://proxy.example.com:8080 \
python examples/advanced_examples.py
```

## Example Workflows

### Basic Search and Fetch
```python
# Search for content
search_args = {"query": "python programming tutorial"}
results = await server._handle_web_search(search_args)

# Fetch content from a URL
fetch_args = {"url": "https://example.com", "format": "markdown"}
content = await server._handle_web_url_read(fetch_args)
```

### Advanced Filtering
```python
search_args = {
    "query": "artificial intelligence news",
    "time_range": "week",  # Last week only
    "language": "en",      # English only
    "safesearch": 1,       # Moderate filtering
}
results = await server._handle_web_search(search_args)
```

### Multiple Formats
```python
formats = ["markdown", "html", "text", "json"]
for format_type in formats:
    fetch_args = {"url": "https://example.com", "format": format_type}
    result = await server._handle_web_url_read(fetch_args)
    # Process result in different formats
```

## Customizing Examples

### Adding New Examples
1. Create a new Python file in the `examples/` directory
2. Import the necessary modules:
```python
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from searxng_search_mcp import SearXNGServer
```

3. Implement your example function:
```python
async def my_custom_example():
    if not os.getenv("SEARXNG_URL"):
        print("SEARXNG_URL environment variable not set")
        return
    
    server = SearXNGServer()
    # Your custom logic here
```

### Modifying Existing Examples
- Change search queries to match your interests
- Adjust time ranges and language filters
- Modify content processing logic
- Add new error handling scenarios

## Performance Considerations

### Large-Scale Testing
- Use the performance benchmarks to test under load
- Monitor memory usage with large content
- Test concurrent request handling
- Analyze response times for optimization

### Production Usage
- Always use built wheels for production
- Implement proper error handling
- Consider rate limiting for high-volume usage
- Monitor SearXNG instance performance

## Troubleshooting

### Common Issues

1. **SEARXNG_URL not set**
   ```bash
   export SEARXNG_URL=https://your-searxng-instance.com
   ```

2. **Connection timeouts**
   - Check your SearXNG instance availability
   - Verify network connectivity
   - Consider increasing timeout values

3. **Authentication errors**
   - Verify username and password
   - Check if your SearXNG instance requires authentication

4. **Proxy issues**
   - Verify proxy URL and port
   - Check proxy authentication if required

### Debug Mode
Add debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To add new examples or improve existing ones:

1. Fork the repository
2. Create a new branch for your examples
3. Add comprehensive documentation
4. Test with different SearXNG instances
5. Submit a pull request

## Best Practices

- Always check for required environment variables
- Implement proper error handling
- Use appropriate timeouts for network operations
- Test with different content types and sizes
- Document your examples clearly
- Consider edge cases and error scenarios