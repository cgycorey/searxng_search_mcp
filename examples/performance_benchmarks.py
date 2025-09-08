#!/usr/bin/env python3
"""
Performance and benchmarking examples for SearXNG Search MCP Server
Tests performance under various conditions
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


async def benchmark_search_performance() -> None:
    """Benchmark search performance with different queries"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("⚡ Search Performance Benchmark")
    print("=" * 40)

    # Test queries of varying complexity
    test_queries = [
        "python",
        "python programming tutorial",
        "advanced python programming techniques for data science",
        "machine learning neural networks deep learning python tensorflow pytorch",
    ]

    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")

        search_args = {
            "query": query,
            "pageno": 1,
            "safesearch": 0,
        }

        # Measure execution time
        start_time = time.time()

        try:
            results = await server._handle_web_search(search_args)
            end_time = time.time()
            execution_time = end_time - start_time

            if results:
                content = results[0].text
                result_count = content.count("**Result")
                content_length = len(content)

                print(f"  ✅ Results: {result_count}")
                print(f"  📊 Content length: {content_length} chars")
                print(f"  ⏱️  Execution time: {execution_time:.3f}s")
                print(
                    f"  📈 Performance: {result_count/max(execution_time, 0.001):.1f} results/s"
                )
            else:
                print("  ❌ No results")

        except Exception as e:
            print(f"  ❌ Error: {e}")


async def benchmark_fetch_performance() -> None:
    """Benchmark content fetching performance"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n⚡ Content Fetch Performance Benchmark")
    print("=" * 40)

    # Test URLs (using example.com for testing)
    test_urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    formats = ["markdown", "html", "text", "json"]

    for url in test_urls:
        print(f"\n🌐 Testing URL: {url}")

        for format_type in formats:
            print(f"  📝 Format: {format_type}")

            fetch_args = {"url": url, "format": format_type}

            # Measure execution time
            start_time = time.time()

            try:
                result = await server._handle_web_url_read(fetch_args)
                end_time = time.time()
                execution_time = end_time - start_time

                if result:
                    content = result[0].text
                    content_length = len(content)

                    print(f"    ✅ Content length: {content_length} chars")
                    print(f"    ⏱️  Execution time: {execution_time:.3f}s")
                    print(
                        f"    📈 Performance: {content_length/max(execution_time, 0.001):.1f} chars/s"
                    )
                else:
                    print("    ❌ No content")

            except Exception as e:
                print(f"    ❌ Error: {e}")


async def benchmark_concurrent_requests() -> None:
    """Benchmark concurrent request handling"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n⚡ Concurrent Request Benchmark")
    print("=" * 40)

    # Test different levels of concurrency
    concurrency_levels = [1, 3, 5, 10]

    for concurrency in concurrency_levels:
        print(f"\n🔄 Testing {concurrency} concurrent requests")

        # Create concurrent search tasks
        tasks = []
        for i in range(concurrency):
            search_args = {
                "query": f"test query {i}",
                "pageno": 1,
                "safesearch": 0,
            }
            tasks.append(server._handle_web_search(search_args))

        # Measure execution time
        start_time = time.time()

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            execution_time = end_time - start_time

            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful

            print(f"  ✅ Successful: {successful}")
            print(f"  ❌ Failed: {failed}")
            print(f"  ⏱️  Total time: {execution_time:.3f}s")
            print(
                f"  📈 Throughput: {successful/max(execution_time, 0.001):.1f} requests/s"
            )

        except Exception as e:
            print(f"  ❌ Error: {e}")


async def stress_test_search() -> None:
    """Stress test search functionality"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🔥 Search Stress Test")
    print("=" * 40)

    # Parameters
    num_requests = 20
    queries = [
        "python programming",
        "machine learning",
        "data science",
        "web development",
        "artificial intelligence",
    ]

    print(f"📊 Executing {num_requests} search requests...")

    # Create stress test tasks
    tasks = []
    for i in range(num_requests):
        query = queries[i % len(queries)]
        search_args = {
            "query": f"{query} test {i}",
            "pageno": 1,
            "safesearch": 0,
        }
        tasks.append(server._handle_web_search(search_args))

    # Run stress test
    start_time = time.time()

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        execution_time = end_time - start_time

        # Analyze results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful

        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏱️  Total time: {execution_time:.3f}s")
        print(f"  📈 Average per request: {execution_time/num_requests:.3f}s")
        print(f"  📊 Success rate: {(successful/num_requests)*100:.1f}%")

    except Exception as e:
        print(f"  ❌ Stress test error: {e}")


async def memory_usage_test() -> None:
    """Test memory usage with large content"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n💾 Memory Usage Test")
    print("=" * 40)

    # Test with different content sizes
    test_urls = [
        "https://example.com",
        "https://example.org",
    ]

    formats = ["text", "json"]

    for url in test_urls:
        print(f"\n🌐 Testing URL: {url}")

        for format_type in formats:
            print(f"  📝 Format: {format_type}")

            fetch_args = {"url": url, "format": format_type}

            try:
                result = await server._handle_web_url_read(fetch_args)

                if result:
                    content = result[0].text
                    content_length = len(content)

                    # Estimate memory usage (rough approximation)
                    memory_mb = content_length / (1024 * 1024)

                    print(f"    ✅ Content length: {content_length} chars")
                    print(f"    💾 Estimated memory: {memory_mb:.2f} MB")

                    if memory_mb > 1:
                        print("    ⚠️  Large content detected")
                    else:
                        print("    ✅ Memory usage normal")

            except Exception as e:
                print(f"    ❌ Error: {e}")


async def main() -> None:
    """Run all performance benchmarks"""
    print("=== SearXNG Search MCP Server - Performance Benchmarks ===\n")

    await benchmark_search_performance()
    await benchmark_fetch_performance()
    await benchmark_concurrent_requests()
    await stress_test_search()
    await memory_usage_test()

    print("\n✅ All performance benchmarks completed!")


if __name__ == "__main__":
    asyncio.run(main())
