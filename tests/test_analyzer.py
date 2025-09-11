"""
Test the search result analyzer functionality.
"""

import json
import os

import pytest

from searxng_search_mcp.analyzer import SearchResultAnalyzer


@pytest.fixture
def analyzer():
    """Create a SearchResultAnalyzer instance for testing."""
    return SearchResultAnalyzer()


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "title": "Python Programming Tutorial - Learn Python Basics",
            "url": "https://example.com/python-tutorial",
            "content": "This comprehensive Python tutorial covers the basics of programming in Python. Learn about variables, functions, and data structures.",
        },
        {
            "title": "Advanced Python Techniques for Developers",
            "url": "https://techblog.com/advanced-python",
            "content": "Explore advanced Python techniques including decorators, generators, and context managers. Perfect for experienced developers.",
        },
        {
            "title": "Python vs JavaScript Comparison 2024",
            "url": "https://comparison.com/python-js",
            "content": "A detailed comparison between Python and JavaScript in 2024. Learn about performance, syntax, and use cases for both languages.",
        },
        {
            "title": "Machine Learning with Python",
            "url": "https://ml-guide.com/python-ml",
            "content": "Discover how to use Python for machine learning applications. This guide covers scikit-learn, TensorFlow, and PyTorch.",
        },
        {
            "title": "Python Web Development Best Practices",
            "url": "https://webdev.com/python-best-practices",
            "content": "Learn best practices for Python web development including frameworks like Django and Flask. Security and performance tips included.",
        },
    ]


class TestSearchResultAnalyzer:
    """Test the SearchResultAnalyzer class."""

    def test_analyzer_initialization(self, analyzer):
        """Test that the analyzer initializes correctly."""
        assert analyzer.max_results == 10
        assert analyzer.min_keyword_freq == 2
        assert isinstance(analyzer.stop_words, set)
        assert len(analyzer.stop_words) > 0

    def test_analyze_summary(self, analyzer, sample_search_results):
        """Test summary analysis functionality."""
        result = analyzer.analyze_search_results(sample_search_results, "summary")

        assert result["analysis_type"] == "summary"
        assert "metrics" in result
        assert "themes" in result
        assert "top_keywords" in result
        assert "top_domains" in result
        assert "insights" in result

        # Check metrics
        metrics = result["metrics"]
        assert metrics["total_results"] == 5
        assert metrics["unique_domains"] == 5
        assert 0 <= metrics["domain_diversity"] <= 1
        assert 0 <= metrics["coverage_score"] <= 1

    def test_analyze_trends(self, analyzer, sample_search_results):
        """Test trends analysis functionality."""
        result = analyzer.analyze_search_results(sample_search_results, "trends")

        assert result["analysis_type"] == "trends"
        assert "temporal_patterns" in result
        assert "emerging_topics" in result
        assert "freshness_indicators" in result
        assert "trend_insights" in result

    def test_analyze_sources(self, analyzer, sample_search_results):
        """Test sources analysis functionality."""
        result = analyzer.analyze_search_results(sample_search_results, "sources")

        assert result["analysis_type"] == "sources"
        assert "domain_distribution" in result
        assert "credibility_scores" in result
        assert "diversity_metrics" in result
        assert "source_recommendations" in result

    def test_analyze_keywords(self, analyzer, sample_search_results):
        """Test keywords analysis functionality."""
        result = analyzer.analyze_search_results(sample_search_results, "keywords")

        assert result["analysis_type"] == "keywords"
        assert "keyword_frequency" in result
        assert "keyword_clusters" in result
        assert "importance_scores" in result
        assert "keyword_insights" in result

    def test_analyze_relevance(self, analyzer, sample_search_results):
        """Test relevance analysis functionality."""
        result = analyzer.analyze_search_results(sample_search_results, "relevance")

        assert result["analysis_type"] == "relevance"
        assert "relevance_scores" in result
        assert "quality_metrics" in result
        assert "average_relevance" in result
        assert "average_quality" in result
        assert "relevance_distribution" in result
        assert "quality_insights" in result

    def test_empty_search_results(self, analyzer):
        """Test handling of empty search results."""
        result = analyzer.analyze_search_results([], "summary")
        assert "error" in result
        assert result["error"] == "No search results provided for analysis"

    def test_invalid_analysis_type(self, analyzer, sample_search_results):
        """Test handling of invalid analysis type."""
        with pytest.raises(ValueError, match="Unsupported analysis type"):
            analyzer.analyze_search_results(sample_search_results, "invalid_type")

    def test_max_results_limit(self, analyzer, sample_search_results):
        """Test that max_results parameter works correctly."""
        # Create more results than the default max
        many_results = sample_search_results * 3  # 15 results

        # Test with default max (10)
        result_default = analyzer.analyze_search_results(many_results, "summary")
        assert result_default["metrics"]["total_results"] == 10

        # Test with custom max (3)
        analyzer.max_results = 3
        result_custom = analyzer.analyze_search_results(many_results, "summary")
        assert result_custom["metrics"]["total_results"] == 3

    def test_domain_extraction(self, analyzer, sample_search_results):
        """Test domain extraction functionality."""
        domains = analyzer._extract_domains(sample_search_results)
        assert len(domains) == 5
        assert "example.com" in domains
        assert "techblog.com" in domains
        assert "comparison.com" in domains
        assert "ml-guide.com" in domains
        assert "webdev.com" in domains

    def test_keyword_extraction(self, analyzer, sample_search_results):
        """Test keyword extraction functionality."""
        keywords = analyzer._extract_keywords(sample_search_results)
        assert len(keywords) > 0
        assert "python" in keywords  # Should appear multiple times
        assert "tutorial" in keywords
        assert "programming" in keywords

    def test_theme_identification(self, analyzer, sample_search_results):
        """Test theme identification functionality."""
        themes = analyzer._identify_themes(sample_search_results)
        assert isinstance(themes, list)
        # Python should be a dominant theme
        assert "python" in themes

    def test_credibility_assessment(self, analyzer, sample_search_results):
        """Test domain credibility assessment."""
        domains = analyzer._extract_domains(sample_search_results)
        credibility_scores = analyzer._assess_domain_credibility(domains)

        assert isinstance(credibility_scores, dict)
        assert len(credibility_scores) == 5
        # All scores should be between 0 and 1
        for score in credibility_scores.values():
            assert 0 <= score <= 1

    def test_json_serialization(self, analyzer, sample_search_results):
        """Test that analysis results can be serialized to JSON."""
        result = analyzer.analyze_search_results(sample_search_results, "summary")

        # Should not raise any exceptions
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

        # Should be able to parse back
        parsed_back = json.loads(json_str)

        # For comparison, we need to convert tuples to lists in the original result
        # since JSON converts tuples to lists
        comparison_result = result.copy()
        if "top_domains" in comparison_result:
            comparison_result["top_domains"] = [
                list(item) if isinstance(item, tuple) else item
                for item in comparison_result["top_domains"]
            ]

        assert parsed_back == comparison_result


def test_analyzer_integration_with_server():
    """Test that analyzer can be integrated with server."""
    # Set required environment variable for test
    original_searxng_url = os.environ.get("SEARXNG_URL")
    os.environ["SEARXNG_URL"] = "https://example.com"

    try:
        from searxng_search_mcp.server_main import SearXNGServer

        server = SearXNGServer()
        assert hasattr(server, "analyzer")
        assert isinstance(server.analyzer, SearchResultAnalyzer)
    finally:
        # Clean up environment variable
        if original_searxng_url is None:
            if "SEARXNG_URL" in os.environ:
                del os.environ["SEARXNG_URL"]
        else:
            os.environ["SEARXNG_URL"] = original_searxng_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
