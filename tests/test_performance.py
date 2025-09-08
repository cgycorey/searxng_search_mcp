"""
Performance and stress tests for SearXNG MCP Server
"""

import asyncio
import os
import time
from unittest.mock import AsyncMock, patch
from typing import List

import pytest
import httpx

from searxng_search_mcp import SearXNGClient, SearXNGServer


@pytest.mark.asyncio
async def test_concurrent_searches() -> None:
    """Test handling multiple concurrent search requests"""
    client = SearXNGClient("https://test.example.com")
    
    mock_response = {
        "results": [
            {
                "title": f"Concurrent Result {i}",
                "url": f"https://example.com/{i}",
                "content": f"Content {i}"
            }
            for i in range(10)
        ]
    }
    
    client.search = AsyncMock(return_value=mock_response)
    
    # Create 10 concurrent search requests
    tasks = [
        client.search(f"query {i}")
        for i in range(10)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # All requests should complete successfully
    assert len(results) == 10
    for i, result in enumerate(results):
        assert result == mock_response
    
    # Should complete in reasonable time (concurrently)
    assert end_time - start_time < 5.0  # 5 seconds max for 10 requests


@pytest.mark.asyncio
async def test_concurrent_url_fetches() -> None:
    """Test handling multiple concurrent URL fetch requests"""
    client = SearXNGClient("https://test.example.com")
    
    mock_contents = [
        f"<html><body>Content {i}</body></html>"
        for i in range(10)
    ]
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock different responses for each URL
        def get_side_effect(url):
            import re
            match = re.search(r'/(\d+)$', url)
            if match:
                index = int(match.group(1))
                response = AsyncMock()
                response.text = mock_contents[index]
                response.raise_for_status.return_value = None
                return response
            return AsyncMock()
        
        mock_client.get.side_effect = get_side_effect
        
        # Create 10 concurrent fetch requests
        urls = [f"https://example.com/{i}" for i in range(10)]
        tasks = [client.fetch_url(url) for url in urls]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All requests should complete successfully
        assert len(results) == 10
        for i, result in enumerate(results):
            assert result == mock_contents[i]
        
        # Should complete in reasonable time
        assert end_time - start_time < 5.0


@pytest.mark.asyncio
async def test_large_response_handling() -> None:
    """Test handling of large responses"""
    client = SearXNGClient("https://test.example.com")
    
    # Create a large response (simulate 100 results)
    large_response = {
        "results": [
            {
                "title": f"Large Result {i}",
                "url": f"https://example.com/{i}",
                "content": f"This is content for result {i} " * 20  # Make content longer
            }
            for i in range(100)
        ]
    }
    
    client.search = AsyncMock(return_value=large_response)
    
    start_time = time.time()
    result = await client.search("large query")
    end_time = time.time()
    
    assert len(result["results"]) == 100
    assert end_time - start_time < 3.0  # Should handle large response quickly


@pytest.mark.asyncio
async def test_large_html_content_handling() -> None:
    """Test handling of large HTML content"""
    client = SearXNGClient("https://test.example.com")
    
    # Create large HTML content (simulate a large web page)
    large_html = """
    <html>
        <head><title>Large Page</title></head>
        <body>
            <h1>Large Content</h1>
    """ + "".join([
        f"<p>This is paragraph {i} with some content to make it longer. " * 10 + "</p>\n"
        for i in range(1000)
    ]) + """
        </body>
    </html>
    """
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value.text = large_html
        mock_client.get.return_value.raise_for_status.return_value = None
        
        start_time = time.time()
        result = await client.fetch_url("https://large.example.com")
        end_time = time.time()
        
        assert len(result) > 100000  # Should be a large string
        assert end_time - start_time < 5.0  # Should handle large HTML quickly


@pytest.mark.asyncio
async def test_rate_limiting_simulation() -> None:
    """Test behavior under simulated rate limiting"""
    client = SearXNGClient("https://test.example.com")
    
    # Simulate rate limiting by adding delays
    call_count = 0
    
    async def delayed_search(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count > 3:  # Simulate rate limit after 3 calls
            await asyncio.sleep(0.2)  # Add delay
        
        return {
            "results": [{"title": f"Rate Limited Result {call_count}", "url": "https://example.com"}]
        }
    
    client.search = delayed_search
    
    # Make many requests quickly
    start_time = time.time()
    tasks = [client.search(f"query {i}") for i in range(6)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    assert len(results) == 6
    # Should take longer due to simulated rate limiting
    assert end_time - start_time > 0.1


@pytest.mark.asyncio
async def test_memory_usage_large_dataset() -> None:
    """Test memory usage with large datasets"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()
        
        # Create a very large response
        large_response = {
            "results": [
                {
                    "title": f"Memory Test Result {i}",
                    "url": f"https://example.com/{i}",
                    "content": "x" * 1000  # 1KB per result
                }
                for i in range(1000)  # 1000 results = ~1MB of data
            ]
        }
        
        server.client.search = AsyncMock(return_value=large_response)
        
        # Process the large response
        result = await server._handle_web_search({"query": "memory test"})
        
        assert len(result) == 1
        assert len(result[0].text) > 1000000  # Should be very large
        assert "Memory Test Result 0" in result[0].text
        assert "Memory Test Result 999" in result[0].text


@pytest.mark.asyncio
async def test_timeout_resilience() -> None:
    """Test resilience to timeout scenarios"""
    client = SearXNGClient("https://test.example.com")
    
    # Simulate intermittent timeouts
    timeout_count = 0
    
    async def intermittent_timeout(*args, **kwargs):
        nonlocal timeout_count
        timeout_count += 1
        if timeout_count % 3 == 0:  # Every 3rd request times out
            raise httpx.TimeoutException("Request timeout")
        
        return {
            "results": [{"title": f"Resilient Result {timeout_count}", "url": "https://example.com"}]
        }
    
    client.search = intermittent_timeout
    
    # Make several requests, some should fail
    results = []
    errors = []
    
    for i in range(6):
        try:
            result = await client.search(f"query {i}")
            results.append(result)
        except httpx.TimeoutException:
            errors.append(f"Timeout on request {i}")
    
    # Should have some successful results and some errors
    assert len(results) == 4  # 2 timeouts out of 6 requests
    assert len(errors) == 2


@pytest.mark.asyncio
async def test_server_concurrent_tool_calls() -> None:
    """Test server handling of concurrent tool calls"""
    with patch.dict(os.environ, {"SEARXNG_URL": "https://test.example.com"}):
        server = SearXNGServer()
        
        # Mock responses
        search_response = {
            "results": [{"title": "Concurrent Search", "url": "https://example.com"}]
        }
        html_content = "<html><body>Concurrent Content</body></html>"
        
        server.client.search = AsyncMock(return_value=search_response)
        server.client.fetch_url = AsyncMock(return_value=html_content)
        
        # Create concurrent tool calls
        tasks = [
            server._handle_web_search({"query": f"search {i}"})
            for i in range(5)
        ] + [
            server._handle_web_url_read({"url": f"https://example.com/{i}"})
            for i in range(5)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All should complete successfully
        assert len(results) == 10
        assert end_time - start_time < 3.0  # Should complete quickly


@pytest.mark.asyncio
async def test_benchmark_search_performance() -> None:
    """Benchmark search performance"""
    client = SearXNGClient("https://test.example.com")
    
    mock_response = {
        "results": [
            {"title": "Benchmark Result", "url": "https://example.com", "content": "Benchmark content"}
        ]
    }
    
    client.search = AsyncMock(return_value=mock_response)
    
    # Run benchmark
    iterations = 50
    start_time = time.time()
    
    for i in range(iterations):
        await client.search(f"benchmark query {i}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / iterations
    
    print(f"\nBenchmark Results:")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per search: {avg_time:.4f}s")
    print(f"Searches per second: {iterations / total_time:.2f}")
    
    # Performance assertions
    assert avg_time < 0.1  # Average should be under 100ms
    assert iterations / total_time > 10  # At least 10 searches per second


if __name__ == "__main__":
    print("✅ Performance tests file is ready!")