"""
Simple demonstration of the complete search + analysis workflow.

This shows how the analysis tool integrates with the existing MCP server
and how the LLM would naturally chain the tools together.
"""

from searxng_search_mcp.analyzer import SearchResultAnalyzer


def demonstrate_complete_workflow():
    """Demonstrate the complete workflow from search to analysis."""

    print("🔄 **Complete Search + Analysis Workflow**")
    print("=" * 60)

    # Initialize analyzer
    analyzer = SearchResultAnalyzer()

    # Simulate what metasearch_web would return
    print("\n1️⃣ **Step 1: User Query → metasearch_web Tool**")
    print(
        "User Query: 'Find information about renewable energy trends and analyze sources'"
    )
    print()
    print("🔍 **Raw Search Results (from metasearch_web):**")

    search_results = [
        {
            "title": "Renewable Energy Trends 2024: Solar and Wind Power Growth",
            "url": "https://energy.gov/renewable-trends-2024",
            "content": "Analysis of renewable energy growth in 2024 shows significant increases in solar and wind power installations. Government incentives and technological advances drive adoption.",
        },
        {
            "title": "Solar Energy vs Wind Power: Comparison Guide",
            "url": "https://energy-comparison.com/solar-vs-wind",
            "content": "Detailed comparison between solar and wind energy technologies. Cost analysis, efficiency metrics, and geographical considerations for renewable energy deployment.",
        },
        {
            "title": "The Future of Renewable Energy: Emerging Technologies 2024",
            "url": "https://tech-research.com/renewable-future",
            "content": "Emerging renewable energy technologies including advanced solar panels, offshore wind farms, and energy storage solutions. Latest innovations and market trends analysis.",
        },
        {
            "title": "Renewable Energy Policy and Government Incentives 2024",
            "url": "https://policy-institute.org/energy-policy",
            "content": "Comprehensive overview of renewable energy policies and government incentives in 2024. Tax credits, grants, and regulatory frameworks for clean energy adoption.",
        },
        {
            "title": "Climate Change Impact on Renewable Energy Development",
            "url": "https://climate-research.org/energy-impact",
            "content": "Research on climate change effects on renewable energy development. How environmental factors influence solar, wind, and other renewable energy sources.",
        },
        {
            "title": "Breaking: Major Renewable Energy Project Announced",
            "url": "https://news-energy.com/breaking-project",
            "content": "Breaking news: Major renewable energy project announced with significant investment. Solar farm development expected to power thousands of homes by 2025.",
        },
    ]

    for i, result in enumerate(search_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:100]}...")
        print()

    # Step 2: LLM decides to call analysis tool
    print("\n2️⃣ **Step 2: LLM Decision → analyze_search_results Tool**")
    print("🧠 **LLM Reasoning:**")
    print("✅ User requested 'analyze sources' in query")
    print("✅ Search results obtained from metasearch_web")
    print("✅ Call analyze_search_results with sources analysis type")
    print()

    # Step 3: Perform analysis
    print("3️⃣ **Step 3: Analysis Results (from analyze_search_results):**")
    print("📊 **Sources Analysis:**")

    analysis_result = analyzer.analyze_search_results(search_results, "sources")

    # Display key analysis insights
    print(f"• Total sources analyzed: {analysis_result['metrics']['total_results']}")
    print(f"• Unique domains: {analysis_result['metrics']['unique_domains']}")
    print(
        f"• Source diversity score: {analysis_result['diversity_metrics']['diversity_score']:.2f}"
    )
    print(
        f"• Domain concentration: {analysis_result['diversity_metrics']['concentration_ratio']:.2f}"
    )
    print()

    print("🏢 **Credibility Assessment:**")
    for domain, score in analysis_result["credibility_scores"].items():
        credibility_level = (
            "High" if score >= 0.8 else "Medium" if score >= 0.6 else "Low"
        )
        print(f"• {domain}: {credibility_level} credibility ({score:.2f})")
    print()

    print("📋 **Source Recommendations:**")
    for recommendation in analysis_result["source_recommendations"]:
        print(f"• {recommendation}")
    print()

    # Step 4: Show how LLM combines everything
    print("4️⃣ **Step 4: LLM Combined Response to User**")
    print("-" * 60)
    print("🔍 **Search Results for 'renewable energy trends':**")
    print(
        "I found 6 relevant articles about renewable energy trends, covering solar and wind power growth, policy updates, and emerging technologies."
    )
    print()
    print("📊 **Source Analysis Results:**")
    print()
    print("**Source Credibility Assessment:**")
    print("• **High Credibility Sources:** energy.gov (official government site)")
    print(
        "• **Medium Credibility Sources:** energy-comparison.com, tech-research.com, policy-institute.org, climate-research.org"
    )
    print("• **Lower Credibility Source:** news-energy.com (breaking news site)")
    print()
    print("**Source Diversity Analysis:**")
    print("• Excellent source diversity with 6 different domains")
    print("• No single source dominates the information landscape")
    print("• Mix of government, research, comparison, and news sources")
    print()
    print("**Key Insights:**")
    print(
        "• Most credible information comes from official government sources (.gov domain)"
    )
    print("• Good variety of perspectives including technical, policy, and news angles")
    print("• Recent content indicates active developments in renewable energy sector")
    print(
        "• Mix of established research and breaking news provides comprehensive coverage"
    )
    print()
    print("🎯 **Recommendations:**")
    print("• For policy information: Prioritize energy.gov and policy-institute.org")
    print(
        "• For technical comparisons: Use energy-comparison.com with verification from official sources"
    )
    print(
        "• For latest developments: Cross-reference news-energy.com with established research sources"
    )
    print(
        "• For comprehensive understanding: Combine multiple source types for balanced perspective"
    )


def demonstrate_llm_tool_chaining():
    """Show how LLM chains tools together based on user intent."""

    print("\n\n🔗 **LLM Tool Chaining Examples**")
    print("=" * 60)

    examples = [
        {
            "user_query": "Search for Python programming tutorials and analyze the sources",
            "llm_reasoning": [
                "1. ✅ User wants search + source analysis",
                "2. ✅ Call metasearch_web('Python programming tutorials')",
                "3. ✅ Extract results from search response",
                "4. ✅ Call analyze_search_results(results, 'sources')",
                "5. ✅ Combine search results + source analysis in response",
            ],
        },
        {
            "user_query": "What are the emerging trends in artificial intelligence?",
            "llm_reasoning": [
                "1. ✅ User asks for 'emerging trends' (trend analysis)",
                "2. ✅ Call metasearch_web('artificial intelligence trends')",
                "3. ✅ Extract results from search response",
                "4. ✅ Call analyze_search_results(results, 'trends')",
                "5. ✅ Highlight trends, patterns, and emerging topics",
            ],
        },
        {
            "user_query": "Find information about climate change and give me a summary of key points",
            "llm_reasoning": [
                "1. ✅ User wants search + summary analysis",
                "2. ✅ Call metasearch_web('climate change')",
                "3. ✅ Extract results from search response",
                "4. ✅ Call analyze_search_results(results, 'summary')",
                "5. ✅ Provide search results + thematic summary",
            ],
        },
        {
            "user_query": "Search for machine learning resources",
            "llm_reasoning": [
                "1. ✅ User only wants search, no analysis requested",
                "2. ✅ Call metasearch_web('machine learning resources')",
                "3. ✅ Return raw search results",
                "4. ❌ Do NOT call analysis tool (user didn't ask for it)",
            ],
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. **User Query:** '{example['user_query']}'")
        print("   **LLM Tool Chaining Logic:**")
        for step in example["llm_reasoning"]:
            print(f"   {step}")

    print("\n🎯 **Key Decision Patterns:**")
    print(
        "• **Analysis Keywords:** 'analyze', 'summary', 'trends', 'sources', 'insights', 'patterns'"
    )
    print(
        "• **Question Types:** 'what are the trends?', 'how credible are sources?', 'summarize key points'"
    )
    print("• **Explicit Requests:** User directly asks for analysis or evaluation")
    print(
        "• **Implicit Needs:** User wants comparison, assessment, or deeper understanding"
    )
    print()
    print("🔄 **Tool Flow Decision Tree:**")
    print("``")
    print("User Query")
    print(
        "├── Contains analysis keywords? → Yes → Call metasearch_web + analyze_search_results"
    )
    print("└── Contains analysis keywords? → No  → Call only metasearch_web")
    print("```")


def show_analysis_types_examples():
    """Show examples of when to use each analysis type."""

    print("\n\n📊 **Analysis Types: When to Use Each**")
    print("=" * 60)

    analysis_types = {
        "summary": [
            "User Query: 'Search for Python programming and summarize the key points'",
            "Use Case: User wants overview and main themes from search results",
            "Best For: Getting quick insights, identifying main topics, understanding scope",
        ],
        "trends": [
            "User Query: 'What are the emerging trends in renewable energy?'",
            "Use Case: User wants to identify patterns, temporal changes, and emerging topics",
            "Best For: Understanding developments, identifying new topics, tracking changes over time",
        ],
        "sources": [
            "User Query: 'Find information about AI and check if sources are credible'",
            "Use Case: User wants to evaluate source quality and credibility",
            "Best For: Source verification, credibility assessment, diversity analysis",
        ],
        "keywords": [
            "User Query: 'Search for machine learning and extract key terms'",
            "Use Case: User wants to identify important terms and concepts",
            "Best For: Keyword research, concept mapping, terminology extraction",
        ],
        "relevance": [
            "User Query: 'Search for web development frameworks and rank by quality'",
            "Use Case: User wants to assess content quality and relevance",
            "Best For: Quality assessment, relevance ranking, content evaluation",
        ],
    }

    for analysis_type, details in analysis_types.items():
        print(f"\n🔍 **{analysis_type.upper()} Analysis:**")
        for detail in details:
            print(f"• {detail}")


if __name__ == "__main__":
    demonstrate_complete_workflow()
    demonstrate_llm_tool_chaining()
    show_analysis_types_examples()
