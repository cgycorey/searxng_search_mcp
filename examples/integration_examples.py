#!/usr/bin/env python3
"""
Integration examples for SearXNG Search MCP Server
Shows how to integrate with different applications and workflows
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


async def example_research_assistant() -> None:
    """Example: Research assistant workflow"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("🔬 Research Assistant Example")
    print("=" * 40)

    research_topic = "renewable energy advancements 2024"

    print(f"📚 Researching topic: {research_topic}")

    # Search for recent information
    search_args = {
        "query": research_topic,
        "pageno": 1,
        "time_range": "month",  # Recent information
        "language": "en",
        "safesearch": 0,
    }

    try:
        # Get search results
        search_results = await server._handle_web_search(search_args)
        if not search_results:
            print("❌ No research sources found")
            return

        print("✅ Found research sources")

        # Extract URLs and fetch detailed content
        content = search_results[0].text
        lines = content.split("\n")
        urls = []

        for line in lines:
            if line.startswith("URL: "):
                url = line.replace("URL: ", "").strip()
                urls.append(url)

        print(f"🔍 Analyzing {min(3, len(urls))} top sources...")

        research_summary = []

        for i, url in enumerate(urls[:3]):  # Limit to top 3 sources
            print(f"\n📄 Source {i+1}: {url}")

            try:
                # Fetch content as markdown for easy reading
                fetch_args = {"url": url, "format": "markdown"}
                fetch_result = await server._handle_web_url_read(fetch_args)

                if fetch_result:
                    content = fetch_result[0].text

                    # Extract key information (simplified)
                    lines = content.split("\n")
                    title = "Unknown Title"

                    # Try to find title
                    for line in lines[:10]:
                        if line.startswith("# ") and len(line) > 2:
                            title = line[2:].strip()
                            break

                    # Get first paragraph
                    first_paragraph = ""
                    for line in lines:
                        if line.strip() and not line.startswith("#"):
                            first_paragraph = line.strip()
                            break

                    research_summary.append(
                        {
                            "source": url,
                            "title": title,
                            "snippet": (
                                first_paragraph[:200] + "..."
                                if len(first_paragraph) > 200
                                else first_paragraph
                            ),
                        }
                    )

                    print(f"  📖 Title: {title}")
                    print(f"  📝 Snippet: {first_paragraph[:100]}...")

            except Exception as e:
                print(f"  ❌ Error analyzing source: {e}")

        # Generate summary
        print("\n📊 Research Summary:")
        print("=" * 30)
        print(f"🔍 Topic: {research_topic}")
        print(f"📚 Sources analyzed: {len(research_summary)}")

        for i, source in enumerate(research_summary, 1):
            print(f"\n{i}. {source['title']}")
            print(f"   URL: {source['source']}")
            print(f"   Summary: {source['snippet']}")

    except Exception as e:
        print(f"❌ Research assistant error: {e}")


async def example_news_monitor() -> None:
    """Example: News monitoring workflow"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n📰 News Monitor Example")
    print("=" * 40)

    # Monitor multiple topics
    topics = [
        "artificial intelligence breakthrough",
        "climate change policy",
        "technology market trends",
    ]

    for topic in topics:
        print(f"\n🔍 Monitoring: {topic}")

        search_args = {
            "query": topic,
            "pageno": 1,
            "time_range": "day",  # Today's news
            "language": "en",
            "safesearch": 0,
        }

        try:
            results = await server._handle_web_search(search_args)
            if results:
                content = results[0].text
                # Count results (simplified)
                result_count = content.count("**Result")
                print(f"  📰 Found {result_count} recent articles")

                # Show first result
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("**Result 1:"):
                        if i + 1 < len(lines):
                            title = line.replace("**Result 1: ", "").replace("**", "")
                            print(f"  📰 Top story: {title}")
                        break

        except Exception as e:
            print(f"  ❌ Error monitoring {topic}: {e}")


async def example_content_aggregator() -> None:
    """Example: Content aggregation from multiple sources"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🔄 Content Aggregator Example")
    print("=" * 40)

    # Define search queries for different content types
    queries = {
        "tutorials": "python programming tutorial beginner",
        "articles": "machine learning applications 2024",
        "documentation": "django framework documentation",
    }

    aggregated_content = {}

    for content_type, query in queries.items():
        print(f"\n📚 Aggregating {content_type}...")

        search_args = {
            "query": query,
            "pageno": 1,
            "language": "en",
            "safesearch": 0,
        }

        try:
            results = await server._handle_web_search(search_args)
            if results:
                content = results[0].text
                aggregated_content[content_type] = content

                # Extract URLs for fetching
                lines = content.split("\n")
                urls = [
                    line.replace("URL: ", "").strip()
                    for line in lines
                    if line.startswith("URL: ")
                ]

                print(f"  ✅ Found {len(urls)} sources")

                # Fetch content from first URL
                if urls:
                    try:
                        fetch_args = {"url": urls[0], "format": "json"}
                        fetch_result = await server._handle_web_url_read(fetch_args)

                        if fetch_result:
                            json_content = json.loads(fetch_result[0].text)
                            title = json_content.get("title", "No title")
                            print(f"  📖 Sample: {title}")

                    except Exception as e:
                        print(f"  ❌ Error fetching sample: {e}")

        except Exception as e:
            print(f"  ❌ Error aggregating {content_type}: {e}")

    # Show aggregation summary
    print("\n📊 Aggregation Summary:")
    print("=" * 30)
    for content_type, content in aggregated_content.items():
        result_count = content.count("**Result")
        print(f"📚 {content_type.capitalize()}: {result_count} sources")


async def example_competitive_analysis() -> None:
    """Example: Competitive analysis workflow"""
    if not os.getenv("SEARXNG_URL"):
        print("⚠️  SEARXNG_URL environment variable not set")
        return

    server = SearXNGServer()

    print("\n🏆 Competitive Analysis Example")
    print("=" * 40)

    # Analyze competitors
    companies = ["OpenAI", "Anthropic", "Google DeepMind"]

    for company in companies:
        print(f"\n🔍 Analyzing: {company}")

        # Search for recent news and developments
        search_args = {
            "query": f"{company} latest news developments 2024",
            "pageno": 1,
            "time_range": "month",
            "language": "en",
            "safesearch": 0,
        }

        try:
            results = await server._handle_web_search(search_args)
            if results:
                content = results[0].text

                # Extract key information
                lines = content.split("\n")
                urls = [
                    line.replace("URL: ", "").strip()
                    for line in lines
                    if line.startswith("URL: ")
                ]

                print(f"  📊 Recent developments: {len(urls)} sources")

                # Analyze top source
                if urls:
                    try:
                        fetch_args = {"url": urls[0], "format": "text"}
                        fetch_result = await server._handle_web_url_read(fetch_args)

                        if fetch_result:
                            text_content = fetch_result[0].text
                            # Simple keyword analysis
                            keywords = [
                                "AI",
                                "model",
                                "release",
                                "update",
                                "partnership",
                                "funding",
                            ]
                            found_keywords = [
                                kw
                                for kw in keywords
                                if kw.lower() in text_content.lower()
                            ]

                            if found_keywords:
                                print(f"  🎯 Key themes: {', '.join(found_keywords)}")
                            else:
                                print("  📝 Content analysis available")

                    except Exception as e:
                        print(f"  ❌ Error analyzing source: {e}")

        except Exception as e:
            print(f"  ❌ Error analyzing {company}: {e}")


async def main() -> None:
    """Run all integration examples"""
    print("=== SearXNG Search MCP Server - Integration Examples ===\n")

    await example_research_assistant()
    await example_news_monitor()
    await example_content_aggregator()
    await example_competitive_analysis()

    print("\n✅ All integration examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
