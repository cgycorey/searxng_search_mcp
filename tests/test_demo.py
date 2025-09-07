#!/usr/bin/env python3
"""
Example usage of SearXNG Search MCP Server
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


async def demonstrate_search_and_fetch():
    """Demonstrate search and fetch functionality"""
    
    if not os.getenv('SEARXNG_URL'):
        print("Please set SEARXNG_URL environment variable")
        return
    
    server = SearXNGServer()
    
    print("🔍 Searching for 'artificial intelligence basics'...")
    search_args = {
        "query": "artificial intelligence basics",
        "pageno": 1,
        "safesearch": 0
    }
    
    try:
        # Perform search
        search_results = await server._handle_web_search(search_args)
        
        if search_results and len(search_results) > 0:
            content = search_results[0].text
            print(f"✅ Search completed!\n")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            # Extract first URL
            lines = content.split('\n')
            for line in lines:
                if line.startswith('URL: '):
                    url = line.replace('URL: ', '').strip()
                    print(f"\n🌐 Fetching content from: {url}")
                    
                    try:
                        fetch_args = {"url": url}
                        fetch_result = await server._handle_web_url_read(fetch_args)
                        
                        if fetch_result and len(fetch_result) > 0:
                            fetched_content = fetch_result[0].text
                            print(f"✅ Successfully fetched {len(fetched_content)} characters")
                            print(f"📝 First 200 characters:")
                            print("-" * 40)
                            print(fetched_content[:200] + "..." if len(fetched_content) > 200 else fetched_content)
                            print("-" * 40)
                        else:
                            print("❌ No content fetched")
                    except Exception as e:
                        print(f"❌ Error fetching URL: {e}")
                    break
        else:
            print("❌ No search results")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    print("=== SearXNG Search MCP Server Example ===\n")
    await demonstrate_search_and_fetch()
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())