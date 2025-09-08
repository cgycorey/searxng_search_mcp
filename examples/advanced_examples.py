#!/usr/bin/env python3
"""
Advanced examples for SearXNG Search MCP Server
Demonstrates various use cases and configurations
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


async def example_basic_search() -> None:
    """Example: Basic web search"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("🔍 Basic Search Example")
    print("=" * 40)

    search_args = {
        "query": "python programming best practices",
        "pageno": 1,
        "safesearch": 0,
    }

    try:
        results = await server._handle_web_search(search_args)
        if results:
            print("✅ Search results:")
            print(
                results[0].text[:500] + "..."
                if len(results[0].text) > 500
                else results[0].text
            )
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_filtered_search() -> None:
    """Example: Search with time and language filters"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🔍 Filtered Search Example")
    print("=" * 40)

    search_args = {
        "query": "artificial intelligence news",
        "pageno": 1,
        "time_range": "week",  # Last week only
        "language": "en",  # English results only
        "safesearch": 1,  # Moderate safe search
    }

    try:
        results = await server._handle_web_search(search_args)
        if results:
            print("✅ Filtered search results:")
            print(
                results[0].text[:500] + "..."
                if len(results[0].text) > 500
                else results[0].text
            )
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_content_formats() -> None:
    """Example: Fetch content in different formats"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🌐 Content Format Examples")
    print("=" * 40)

    test_url = "https://example.com"
    formats = ["markdown", "html", "text", "json"]

    for format_type in formats:
        print(f"\n📝 Format: {format_type.upper()}")
        try:
            fetch_args = {"url": test_url, "format": format_type}
            result = await server._handle_web_url_read(fetch_args)
            if result:
                content = result[0].text
                print(f"✅ Success ({len(content)} characters)")
                if format_type == "json":
                    # Pretty print JSON
                    parsed = json.loads(content)
                    print(json.dumps(parsed, indent=2)[:200] + "...")
                else:
                    print(content[:200] + "..." if len(content) > 200 else content)
        except Exception as e:
            print(f"❌ Error: {e}")


async def example_raw_content() -> None:
    """Example: Fetch raw HTML content"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🔧 Raw Content Example")
    print("=" * 40)

    test_url = "https://example.com"
    fetch_args = {"url": test_url, "raw": True}

    try:
        result = await server._handle_web_url_read(fetch_args)
        if result:
            content = result[0].text
            print(f"✅ Raw HTML content ({len(content)} characters):")
            print(content[:300] + "..." if len(content) > 300 else content)
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_search_and_fetch_workflow() -> None:
    """Example: Complete workflow - search then fetch content"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🔄 Complete Workflow Example")
    print("=" * 40)

    # Step 1: Search
    print("Step 1: Searching for 'machine learning tutorials'...")
    search_args = {
        "query": "machine learning tutorials for beginners",
        "pageno": 1,
        "safesearch": 0,
    }

    try:
        search_results = await server._handle_web_search(search_args)
        if not search_results:
            print("❌ No search results found")
            return

        # Extract first URL from search results
        content = search_results[0].text
        lines = content.split("\n")
        first_url = None

        for line in lines:
            if line.startswith("URL: "):
                first_url = line.replace("URL: ", "").strip()
                break

        if not first_url:
            print("❌ No URL found in search results")
            return

        print(f"✅ Found URL: {first_url}")

        # Step 2: Fetch content in multiple formats
        print("\nStep 2: Fetching content in different formats...")
        formats = ["markdown", "json"]

        for format_type in formats:
            print(f"\n📄 Fetching as {format_type}...")
            fetch_args = {"url": first_url, "format": format_type}

            try:
                fetch_result = await server._handle_web_url_read(fetch_args)
                if fetch_result:
                    fetched_content = fetch_result[0].text
                    print(
                        f"✅ Successfully fetched ({len(fetched_content)} characters)"
                    )

                    if format_type == "json":
                        # Parse and show structure
                        parsed = json.loads(fetched_content)
                        print("📊 JSON structure:")
                        for key in parsed.keys():
                            value_type = type(parsed[key]).__name__
                            if key in ["title", "url"]:
                                print(f"  {key}: {parsed[key]}")
                            else:
                                print(
                                    f"  {key}: {value_type} ({len(str(parsed[key]))} chars)"
                                )
                    else:
                        print("📝 Preview:")
                        preview = (
                            fetched_content[:150] + "..."
                            if len(fetched_content) > 150
                            else fetched_content
                        )
                        print(f"  {preview}")

            except Exception as e:
                print(f"❌ Error fetching {format_type}: {e}")

    except Exception as e:
        print(f"❌ Error in workflow: {e}")


async def example_error_handling() -> None:
    """Example: Error handling scenarios"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n⚠️  Error Handling Examples")
    print("=" * 40)

    # Test 1: Empty search query
    print("Test 1: Empty search query")
    try:
        result = await server._handle_web_search({"query": ""})
        if result:
            print(f"✅ Handled empty query: {result[0].text}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 2: Invalid URL
    print("\nTest 2: Invalid URL")
    try:
        result = await server._handle_web_url_read({"url": "not-a-valid-url"})
        if result:
            print(f"✅ Handled invalid URL: {result[0].text}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Empty URL
    print("\nTest 3: Empty URL")
    try:
        result = await server._handle_web_url_read({"url": ""})
        if result:
            print(f"✅ Handled empty URL: {result[0].text}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main() -> None:
    """Run all examples"""
    print("=== SearXNG Search MCP Server - Advanced Examples ===\n")

    await example_basic_search()
    await example_filtered_search()
    await example_content_formats()
    await example_raw_content()
    await example_search_and_fetch_workflow()
    await example_error_handling()

    print("\n✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
