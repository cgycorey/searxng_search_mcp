"""
Demonstration of the complete search + analysis flow.

This example shows how the LLM would naturally chain the tools together
to provide comprehensive search results with intelligent analysis.
"""

from searxng_search_mcp.analyzer import SearchResultAnalyzer


def demonstrate_analysis_flow():
    """Demonstrate how search and analysis tools work together."""

    # Simulate search results from metasearch_web tool
    mock_search_results = [
        {
            "title": "Python Programming Tutorial - Complete Guide 2024",
            "url": "https://docs.python.org/tutorial",
            "content": "This comprehensive Python tutorial covers everything from basics to advanced concepts. Learn variables, functions, classes, and modern Python features.",
        },
        {
            "title": "JavaScript vs Python: Which is Better in 2024?",
            "url": "https://techcomparison.com/js-vs-python",
            "content": "Detailed comparison between JavaScript and Python for web development, data science, and machine learning applications.",
        },
        {
            "title": "Machine Learning with Python: A Beginner's Guide",
            "url": "https://ml-guide.com/python-ml",
            "content": "Learn machine learning fundamentals using Python. This guide covers scikit-learn, TensorFlow, and practical ML applications.",
        },
        {
            "title": "Python Web Development: Django vs Flask",
            "url": "https://webdev.com/python-frameworks",
            "content": "Comprehensive comparison of Django and Flask frameworks for Python web development. Performance, scalability, and use cases analyzed.",
        },
        {
            "title": "Python for Data Science: Complete Tutorial",
            "url": "https://datascience.com/python-tutorial",
            "content": "Master Python for data science with pandas, numpy, matplotlib, and statistical analysis techniques.",
        },
    ]

    # Initialize analyzer
    analyzer = SearchResultAnalyzer()

    print("🔍 **Search Results Analysis Flow Demonstration**")
    print("=" * 60)

    # Step 1: Show raw search results (what metasearch_web returns)
    print("\n1️⃣ **Step 1: Raw Search Results (from metasearch_web)**")
    print(f"   Found {len(mock_search_results)} results")
    for i, result in enumerate(mock_search_results, 1):
        print(f"   {i}. {result['title']}")
        print(f"      URL: {result['url']}")
        print(f"      Content: {result['content'][:100]}...")
        print()

    # Step 2: Perform different types of analysis
    print("\n2️⃣ **Step 2: Analysis Results (from analyze_search_results)**")
    print("-" * 60)

    # Summary Analysis
    print("\n📊 **Summary Analysis:**")
    summary_result = analyzer.analyze_search_results(mock_search_results, "summary")
    print(f"   • Total results analyzed: {summary_result['metrics']['total_results']}")
    print(f"   • Unique domains: {summary_result['metrics']['unique_domains']}")
    print(f"   • Domain diversity: {summary_result['metrics']['domain_diversity']:.2f}")
    print(f"   • Main themes: {', '.join(summary_result['themes'])}")
    print(
        f"   • Top keywords: {', '.join([kw['keyword'] for kw in summary_result['top_keywords'][:5]])}"
    )

    # Sources Analysis
    print("\n🏢 **Sources Analysis:**")
    sources_result = analyzer.analyze_search_results(mock_search_results, "sources")
    print(
        f"   • Source diversity score: {sources_result['diversity_metrics']['diversity_score']:.2f}"
    )
    print(
        f"   • Top domains: {', '.join([domain for domain, _ in sources_result['domain_distribution']['top_domains'][:3]])}"
    )

    # Show credibility scores
    print("   • Credibility scores:")
    for domain, score in list(sources_result["credibility_scores"].items())[:3]:
        credibility_level = (
            "High" if score >= 0.8 else "Medium" if score >= 0.6 else "Low"
        )
        print(f"     - {domain}: {credibility_level} ({score:.2f})")

    # Keywords Analysis
    print("\n🔑 **Keywords Analysis:**")
    keywords_result = analyzer.analyze_search_results(mock_search_results, "keywords")
    print(f"   • Total unique keywords: {len(keywords_result['keyword_frequency'])}")
    print(f"   • Keyword clusters found: {len(keywords_result['keyword_clusters'])}")
    print("   • Top keywords by importance:")
    for keyword, importance in sorted(
        keywords_result["importance_scores"].items(), key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"     - {keyword}: {importance:.3f}")

    # Trends Analysis
    print("\n📈 **Trends Analysis:**")
    trends_result = analyzer.analyze_search_results(mock_search_results, "trends")
    print(
        f"   • Recent content indicators: {trends_result['freshness_indicators']['fresh_content']}"
    )
    print(
        f"   • Evergreen content: {trends_result['freshness_indicators']['evergreen_content']}"
    )
    print(
        f"   • Emerging topics: {', '.join([topic['topic'] for topic in trends_result['emerging_topics'][:5]])}"
    )

    # Relevance Analysis
    print("\n🎯 **Relevance Analysis:**")
    relevance_result = analyzer.analyze_search_results(mock_search_results, "relevance")
    print(f"   • Average relevance score: {relevance_result['average_relevance']:.2f}")
    print(f"   • Average quality score: {relevance_result['average_quality']:.2f}")
    print("   • Relevance distribution:")
    for category, count in relevance_result["relevance_distribution"].items():
        print(f"     - {category}: {count} results")

    # Step 3: Show how LLM would combine everything
    print("\n3️⃣ **Step 3: How LLM Combines Search + Analysis**")
    print("-" * 60)
    print("The LLM would provide a response like:")
    print()
    print("🔍 **Search Results for 'Python programming':**")
    print(
        "I found 5 relevant results about Python programming covering tutorials, comparisons, and applications."
    )
    print()
    print("📊 **Key Insights from Analysis:**")
    print(
        "• **Main Themes**: Python is prominently featured across tutorials, comparisons, and applications"
    )
    print(
        "• **Source Quality**: High diversity of sources with good credibility scores"
    )
    print(
        "• **Content Focus**: Strong emphasis on web development, data science, and machine learning"
    )
    print(
        "• **Trending Topics**: Python vs JavaScript comparisons and ML applications are emerging"
    )
    print()
    print("🏢 **Top Sources:**")
    print("• docs.python.org (High credibility - official documentation)")
    print("• techcomparison.com (Medium credibility - comparison site)")
    print("• ml-guide.com (Medium credibility - educational content)")
    print()
    print("🎯 **Recommendations:**")
    print("• For learning: Start with official Python documentation")
    print(
        "• For comparisons: JavaScript vs Python analysis shows Python excels in data science"
    )
    print(
        "• For applications: Machine learning and web development are strong use cases"
    )


def demonstrate_llm_decision_flow():
    """Show how LLM decides to use analysis tool."""

    print("\n\n🧠 **LLM Decision Flow for Tool Usage**")
    print("=" * 60)

    scenarios = [
        {
            "query": "Search for AI trends and analyze the results",
            "reasoning": [
                "✅ User explicitly requests 'analyze the results'",
                "✅ Call metasearch_web('AI trends') first",
                "✅ Then call analyze_search_results(results, 'summary')",
                "✅ Provide combined search + analysis response",
            ],
        },
        {
            "query": "Find information about climate change and check source credibility",
            "reasoning": [
                "✅ User wants to 'check source credibility'",
                "✅ Call metasearch_web('climate change') first",
                "✅ Then call analyze_search_results(results, 'sources')",
                "✅ Focus response on credibility assessment",
            ],
        },
        {
            "query": "What are the emerging topics in machine learning?",
            "reasoning": [
                "✅ User asks for 'emerging topics' (trend analysis)",
                "✅ Call metasearch_web('machine learning topics') first",
                "✅ Then call analyze_search_results(results, 'trends')",
                "✅ Highlight emerging topics and patterns",
            ],
        },
        {
            "query": "Search for Python programming tutorials",
            "reasoning": [
                "❌ User only requests search, no analysis mentioned",
                "✅ Call only metasearch_web('Python programming tutorials')",
                "❌ Do NOT call analysis tool unless user follows up",
            ],
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. **Query:** '{scenario['query']}'")
        print("   **LLM Reasoning:**")
        for step in scenario["reasoning"]:
            print(f"   {step}")

    print("\n🎯 **Key Decision Factors:**")
    print("• User explicitly mentions analysis keywords → Use analysis tool")
    print("• User asks for insights/patterns → Use analysis tool")
    print("• User requests source evaluation → Use analysis tool with 'sources' type")
    print("• User wants trends/comparisons → Use analysis tool with 'trends' type")
    print("• User only wants raw search results → Skip analysis tool")


if __name__ == "__main__":
    demonstrate_analysis_flow()
    demonstrate_llm_decision_flow()
