#!/usr/bin/env python3
"""
Test script to demonstrate multiple content format support
"""

import os
import asyncio
import sys
import json
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from searxng_search_mcp import SearXNGServer


async def test_multiple_formats():
    """Test fetching content in different formats"""
    
    if not os.getenv('SEARXNG_URL'):
        print("Please set SEARXNG_URL environment variable")
        return
    
    server = SearXNGServer()
    
    test_url = "https://httpbin.org/html"
    formats = ["markdown", "html", "text", "json"]
    
    print(f"🧪 Testing URL: {test_url}")
    print("=" * 60)
    
    for fmt in formats:
        print(f"\n📋 Format: {fmt.upper()}")
        print("-" * 40)
        
        try:
            if fmt == "json":
                # Test JSON format
                fetch_args = {"url": test_url, "format": "json"}
                result = await server._handle_web_url_read(fetch_args)
                
                if result and len(result) > 0:
                    content = result[0].text
                    # Parse and pretty print the JSON
                    try:
                        parsed = json.loads(content)
                        print(f"✅ JSON structure with keys: {list(parsed.keys())}")
                        print(f"📄 Title: {parsed.get('title', 'No title')}")
                        print(f"📏 Content length: {len(parsed.get('content', ''))}")
                        print(f"📊 Metadata: {parsed.get('metadata', {})}")
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON returned")
                else:
                    print("❌ No content returned")
            else:
                # Test other formats
                fetch_args = {"url": test_url, "format": fmt}
                result = await server._handle_web_url_read(fetch_args)
                
                if result and len(result) > 0:
                    content = result[0].text
                    print(f"✅ Content length: {len(content)} characters")
                    print(f"📝 Preview (first 150 characters):")
                    print("-" * 30)
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(preview)
                    print("-" * 30)
                else:
                    print("❌ No content returned")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 Testing RAW mode")
    print("-" * 40)
    
    try:
        # Test raw mode
        fetch_args = {"url": test_url, "raw": True}
        result = await server._handle_web_url_read(fetch_args)
        
        if result and len(result) > 0:
            content = result[0].text
            print(f"✅ Raw content length: {len(content)} characters")
            print(f"📝 Contains HTML tags: {'<' in content and '>' in content}")
            print(f"📝 Preview (first 150 characters):")
            print("-" * 30)
            preview = content[:150] + "..." if len(content) > 150 else content
            print(preview)
            print("-" * 30)
        else:
            print("❌ No content returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    print("=== Multiple Format Support Test ===\n")
    await test_multiple_formats()
    print("\n✅ Format testing completed!")


if __name__ == "__main__":
    asyncio.run(main())