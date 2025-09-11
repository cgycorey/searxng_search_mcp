"""
Search Result Analysis Module

This module provides intelligent analysis of search results, extracting insights,
patterns, and actionable information from raw search data.

Key Features:
    - Multiple analysis types (summary, trends, sources, keywords, relevance)
    - Configurable analysis parameters
    - Statistical analysis and pattern recognition
    - Domain credibility assessment
    - Keyword extraction and clustering
    - Coverage and diversity metrics

Analysis Types:
    - summary: Overview with themes, sources, coverage metrics
    - trends: Temporal patterns and emerging topics
    - sources: Domain analysis and credibility assessment
    - keywords: Keyword extraction and clustering
    - relevance: Content quality and relevance scoring
"""

import logging
import re
from collections import Counter
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SearchResultAnalyzer:
    """
    Intelligent search result analyzer that provides insights and patterns.

    This class analyzes search results to extract meaningful information,
    identify trends, assess source credibility, and provide actionable insights.

    Attributes:
        max_results (int): Maximum number of results to analyze
        min_keyword_freq (int): Minimum frequency for keyword inclusion
        stop_words (set): Common words to exclude from keyword analysis
    """

    def __init__(self, max_results: int = 10, min_keyword_freq: int = 2):
        """
        Initialize the search result analyzer.

        Args:
            max_results: Maximum number of results to analyze (default: 10)
            min_keyword_freq: Minimum frequency for keyword inclusion (default: 2)
        """
        self.max_results = max_results
        self.min_keyword_freq = min_keyword_freq

        # Common English stop words
        self.stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "them",
            "their",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "some",
            "any",
            "few",
            "more",
            "most",
            "other",
            "such",
            "no",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "now",
        }

    def analyze_search_results(
        self, search_results: List[Dict[str, Any]], analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Analyze search results based on the specified analysis type.

        Args:
            search_results: List of search result dictionaries
            analysis_type: Type of analysis to perform
                          (summary, trends, sources, keywords, relevance)

        Returns:
            Dictionary containing analysis results and insights

        Raises:
            ValueError: If analysis_type is not supported
        """
        if not search_results:
            return {"error": "No search results provided for analysis"}

        # Limit results to max_results
        results = search_results[: self.max_results]

        if analysis_type == "summary":
            return self._analyze_summary(results)
        elif analysis_type == "trends":
            return self._analyze_trends(results)
        elif analysis_type == "sources":
            return self._analyze_sources(results)
        elif analysis_type == "keywords":
            return self._analyze_keywords(results)
        elif analysis_type == "relevance":
            return self._analyze_relevance(results)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")

    def _analyze_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive summary analysis."""
        logger.debug("Performing summary analysis")

        # Extract basic metrics
        total_results = len(results)
        domains = self._extract_domains(results)
        unique_domains = len(set(domains))

        # Extract keywords
        all_keywords = self._extract_keywords(results)
        top_keywords = Counter(all_keywords).most_common(10)

        # Generate themes from titles and content
        themes = self._identify_themes(results)

        # Calculate coverage metrics
        coverage_score = self._calculate_coverage(results)

        return {
            "analysis_type": "summary",
            "metrics": {
                "total_results": total_results,
                "unique_domains": unique_domains,
                "domain_diversity": (
                    unique_domains / total_results if total_results > 0 else 0
                ),
                "coverage_score": coverage_score,
            },
            "themes": themes,
            "top_keywords": [
                {"keyword": kw, "frequency": freq} for kw, freq in top_keywords
            ],
            "top_domains": Counter(domains).most_common(5),
            "insights": self._generate_summary_insights(results, themes, top_keywords),
        }

    def _analyze_trends(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns and emerging topics."""
        logger.debug("Performing trends analysis")

        # Extract temporal indicators from content
        temporal_patterns = self._extract_temporal_patterns(results)

        # Identify emerging topics based on keyword frequency
        keywords = self._extract_keywords(results)
        keyword_trends = Counter(keywords).most_common(15)

        # Analyze content freshness indicators
        freshness_indicators = self._analyze_freshness(results)

        return {
            "analysis_type": "trends",
            "temporal_patterns": temporal_patterns,
            "emerging_topics": [
                {"topic": kw, "score": freq} for kw, freq in keyword_trends
            ],
            "freshness_indicators": freshness_indicators,
            "trend_insights": self._generate_trend_insights(results, keyword_trends),
        }

    def _analyze_sources(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze domain credibility and source distribution."""
        logger.debug("Performing sources analysis")

        domains = self._extract_domains(results)
        domain_stats = self._analyze_domain_statistics(domains)

        # Assess credibility based on domain characteristics
        credibility_scores = self._assess_domain_credibility(domains)

        # Calculate source diversity
        diversity_metrics = self._calculate_source_diversity(results)

        return {
            "analysis_type": "sources",
            "domain_distribution": domain_stats,
            "credibility_scores": credibility_scores,
            "diversity_metrics": diversity_metrics,
            "source_recommendations": self._generate_source_recommendations(
                credibility_scores
            ),
        }

    def _analyze_keywords(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and analyze keywords with clustering."""
        logger.debug("Performing keywords analysis")

        # Extract keywords from all results
        all_keywords = self._extract_keywords(results)
        keyword_freq = Counter(all_keywords)

        # Filter by minimum frequency
        filtered_keywords = {
            k: v for k, v in keyword_freq.items() if v >= self.min_keyword_freq
        }

        # Cluster keywords by semantic similarity
        keyword_clusters = self._cluster_keywords(filtered_keywords)

        # Calculate keyword importance scores
        importance_scores = self._calculate_keyword_importance(
            filtered_keywords, len(results)
        )

        return {
            "analysis_type": "keywords",
            "keyword_frequency": dict(filtered_keywords),
            "keyword_clusters": keyword_clusters,
            "importance_scores": importance_scores,
            "keyword_insights": self._generate_keyword_insights(
                filtered_keywords, keyword_clusters
            ),
        }

    def _analyze_relevance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content quality and relevance scoring."""
        logger.debug("Performing relevance analysis")

        relevance_scores = []
        quality_metrics = []

        for result in results:
            # Calculate relevance score
            relevance = self._calculate_relevance_score(result)
            relevance_scores.append(relevance)

            # Assess content quality
            quality = self._assess_content_quality(result)
            quality_metrics.append(quality)

        # Aggregate metrics
        avg_relevance = (
            sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        )
        avg_quality = (
            sum(quality_metrics) / len(quality_metrics) if quality_metrics else 0
        )

        return {
            "analysis_type": "relevance",
            "relevance_scores": relevance_scores,
            "quality_metrics": quality_metrics,
            "average_relevance": avg_relevance,
            "average_quality": avg_quality,
            "relevance_distribution": self._calculate_relevance_distribution(
                relevance_scores
            ),
            "quality_insights": self._generate_quality_insights(
                relevance_scores, quality_metrics
            ),
        }

    def _extract_domains(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract domain names from result URLs."""
        domains = []
        for result in results:
            url = result.get("url", "")
            if url:
                try:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    if domain.startswith("www."):
                        domain = domain[4:]
                    domains.append(domain)
                except Exception:
                    continue
        return domains

    def _extract_keywords(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from titles and content."""
        keywords = []

        for result in results:
            # Extract from title
            title = result.get("title", "").lower()
            title_words = re.findall(r"\b[a-z]{3,}\b", title)
            keywords.extend([w for w in title_words if w not in self.stop_words])

            # Extract from content
            content = result.get("content", "").lower()
            content_words = re.findall(r"\b[a-z]{3,}\b", content)
            keywords.extend([w for w in content_words if w not in self.stop_words])

        return keywords

    def _identify_themes(self, results: List[Dict[str, Any]]) -> List[str]:
        """Identify common themes from search results."""
        themes = []

        # Look for common patterns in titles
        title_words = []
        for result in results:
            title = result.get("title", "").lower()
            words = re.findall(r"\b[a-z]{4,}\b", title)
            title_words.extend([w for w in words if w not in self.stop_words])

        # Find most common words as potential themes
        word_freq = Counter(title_words)
        themes = [word for word, freq in word_freq.most_common(5) if freq >= 2]

        return themes

    def _calculate_coverage(self, results: List[Dict[str, Any]]) -> float:
        """Calculate coverage score based on content completeness."""
        if not results:
            return 0.0

        total_score = 0.0
        for result in results:
            score = 0.0

            # Check for title
            if result.get("title"):
                score += 0.3

            # Check for URL
            if result.get("url"):
                score += 0.2

            # Check for content
            content = result.get("content", "")
            if len(content) > 50:
                score += 0.5

            total_score += score

        return total_score / len(results)

    def _extract_temporal_patterns(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract temporal patterns from content."""
        patterns = {
            "recent_indicators": 0,
            "historical_references": 0,
            "time_sensitive_content": 0,
        }

        for result in results:
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            text = f"{title} {content}"

            # Look for recent indicators
            recent_words = [
                "recent",
                "latest",
                "new",
                "now",
                "today",
                "current",
                "breaking",
            ]
            if any(word in text for word in recent_words):
                patterns["recent_indicators"] += 1

            # Look for historical references
            historical_words = [
                "history",
                "historical",
                "past",
                "former",
                "previous",
                "old",
            ]
            if any(word in text for word in historical_words):
                patterns["historical_references"] += 1

            # Look for time-sensitive content
            time_words = [
                "deadline",
                "schedule",
                "timeline",
                "date",
                "when",
                "soon",
                "upcoming",
            ]
            if any(word in text for word in time_words):
                patterns["time_sensitive_content"] += 1

        return patterns

    def _analyze_freshness(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content freshness indicators."""
        freshness = {
            "fresh_content": 0,
            "evergreen_content": 0,
            "outdated_indicators": 0,
        }

        for result in results:
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            text = f"{title} {content}"

            # Fresh content indicators
            fresh_words = ["2023", "2024", "2025", "recently", "just", "new", "latest"]
            if any(word in text for word in fresh_words):
                freshness["fresh_content"] += 1

            # Evergreen content indicators
            evergreen_words = [
                "guide",
                "tutorial",
                "how to",
                "basics",
                "fundamentals",
                "introduction",
            ]
            if any(word in text for word in evergreen_words):
                freshness["evergreen_content"] += 1

            # Outdated content indicators
            outdated_words = ["2020", "2021", "2022", "old", "previous", "former"]
            if any(word in text for word in outdated_words):
                freshness["outdated_indicators"] += 1

        return freshness

    def _analyze_domain_statistics(self, domains: List[str]) -> Dict[str, Any]:
        """Analyze domain distribution statistics."""
        if not domains:
            return {}

        domain_counts = Counter(domains)
        total_domains = len(domains)
        unique_domains = len(domain_counts)

        return {
            "total_domains": total_domains,
            "unique_domains": unique_domains,
            "domain_concentration": float(max(domain_counts.values()) / total_domains),
            "top_domains": domain_counts.most_common(10),
            "domain_distribution": dict(domain_counts),
        }

    def _assess_domain_credibility(self, domains: List[str]) -> Dict[str, float]:
        """Assess credibility scores for domains."""
        credibility_scores = {}

        # Known credible domains (simplified assessment)
        credible_domains = {
            "wikipedia.org",
            "github.com",
            "stackoverflow.com",
            "medium.com",
            "techcrunch.com",
            "bbc.com",
            "cnn.com",
            "reuters.com",
            "apnews.com",
            "nature.com",
            "science.org",
            "arxiv.org",
            "ieee.org",
            "acm.org",
        }

        # Known less credible domains
        less_credible = {"clickbait.com", "fakenews.com", "unreliablesource.com"}

        domain_counts = Counter(domains)

        for domain in domain_counts:
            score = 0.5  # Neutral score

            if domain in credible_domains:
                score = 0.9
            elif domain in less_credible:
                score = 0.2
            elif any(tld in domain for tld in [".edu", ".gov", ".org"]):
                score = 0.8
            elif any(tld in domain for tld in [".com", ".net", ".co"]):
                score = 0.6

            credibility_scores[domain] = score

        return credibility_scores

    def _calculate_source_diversity(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate source diversity metrics."""
        domains = self._extract_domains(results)
        domain_counts = Counter(domains)

        if not domains:
            return {"diversity_score": 0.0, "concentration_ratio": 0.0}

        # Herfindahl-Hirschman Index (HHI) for concentration
        total = len(domains)
        hhi = sum((count / total) ** 2 for count in domain_counts.values())

        # Diversity score (inverse of concentration)
        diversity_score = 1 - hhi

        # Concentration ratio (top 3 domains)
        top_3_share = sum(count for _, count in domain_counts.most_common(3)) / total

        return {
            "diversity_score": diversity_score,
            "concentration_ratio": top_3_share,
            "unique_source_ratio": len(domain_counts) / total,
        }

    def _cluster_keywords(self, keywords: Dict[str, int]) -> Dict[str, List[str]]:
        """Cluster keywords by semantic similarity (simplified)."""
        clusters: Dict[str, List[str]] = {}

        # Simple clustering based on common prefixes/suffixes
        for keyword in keywords:
            cluster_key = keyword[:4]  # Use first 4 characters as cluster key

            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(keyword)

        # Filter out clusters with only one keyword
        return {k: v for k, v in clusters.items() if len(v) > 1}

    def _calculate_keyword_importance(
        self, keywords: Dict[str, int], total_results: int
    ) -> Dict[str, float]:
        """Calculate importance scores for keywords."""
        importance_scores: Dict[str, float] = {}

        if not keywords or total_results == 0:
            return importance_scores

        max_freq = max(keywords.values())

        for keyword, freq in keywords.items():
            # Normalize frequency
            normalized_freq = freq / max_freq

            # Calculate document frequency (how many results contain this keyword)
            doc_freq = freq / total_results

            # Combine metrics for importance score
            importance = (normalized_freq * 0.7) + (doc_freq * 0.3)
            importance_scores[keyword] = round(importance, 3)

        return importance_scores

    def _calculate_relevance_score(self, result: Dict[str, Any]) -> float:
        """Calculate relevance score for a single result."""
        score = 0.0

        # Title relevance
        title = result.get("title", "")
        if title:
            score += 0.3

        # Content length and quality
        content = result.get("content", "")
        if len(content) > 100:
            score += 0.2
        if len(content) > 300:
            score += 0.2

        # URL quality
        url = result.get("url", "")
        if url and url.startswith(("http://", "https://")):
            score += 0.1

        # Content uniqueness (simplified)
        if content and len(set(content.split())) > 20:
            score += 0.2

        return min(score, 1.0)

    def _assess_content_quality(self, result: Dict[str, Any]) -> float:
        """Assess content quality for a single result."""
        quality = 0.0

        content = result.get("content", "")
        if not content:
            return 0.0

        # Length quality
        if 50 <= len(content) <= 1000:
            quality += 0.3
        elif 1000 < len(content) <= 3000:
            quality += 0.4

        # Readability (simplified - check for sentence structure)
        sentences = content.split(".")
        if len(sentences) > 3:
            quality += 0.2

        # Information density
        words = content.split()
        if len(words) > 20:
            quality += 0.2

        # Structure (presence of punctuation)
        if any(char in content for char in [",", ";", ":", "-"]):
            quality += 0.1

        return min(quality, 1.0)

    def _calculate_relevance_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of relevance scores."""
        distribution = {
            "high_relevance": 0,  # 0.8 - 1.0
            "medium_relevance": 0,  # 0.5 - 0.8
            "low_relevance": 0,  # 0.0 - 0.5
        }

        for score in scores:
            if score >= 0.8:
                distribution["high_relevance"] += 1
            elif score >= 0.5:
                distribution["medium_relevance"] += 1
            else:
                distribution["low_relevance"] += 1

        return distribution

    def _generate_summary_insights(
        self, results: List[Dict[str, Any]], themes: List[str], keywords: List[tuple]
    ) -> List[str]:
        """Generate insights for summary analysis."""
        insights = []

        if len(results) < 5:
            insights.append(
                "Limited number of results available for comprehensive analysis"
            )

        if len(set(self._extract_domains(results))) == 1:
            insights.append("All results from single domain - limited source diversity")

        if themes:
            insights.append(f"Primary themes identified: {', '.join(themes[:3])}")

        if keywords and keywords[0][1] > len(results) * 0.5:
            insights.append(
                f"Dominant keyword: '{keywords[0][0]}' appears in majority of results"
            )

        return insights

    def _generate_trend_insights(
        self, results: List[Dict[str, Any]], keywords: List[tuple]
    ) -> List[str]:
        """Generate insights for trends analysis."""
        insights = []

        recent_count = sum(
            1
            for r in results
            if any(
                word in r.get("content", "").lower()
                for word in ["recent", "latest", "new", "now"]
            )
        )

        if recent_count > len(results) * 0.5:
            insights.append("Majority of results contain recent/timely information")

        if keywords:
            top_keyword = keywords[0][0]
            insights.append(f"Trending topic: '{top_keyword}' appears most frequently")

        return insights

    def _generate_source_recommendations(
        self, credibility_scores: Dict[str, float]
    ) -> List[str]:
        """Generate source recommendations based on credibility."""
        recommendations = []

        high_credibility = [
            domain for domain, score in credibility_scores.items() if score >= 0.8
        ]
        low_credibility = [
            domain for domain, score in credibility_scores.items() if score < 0.4
        ]

        if high_credibility:
            recommendations.append(
                f"High credibility sources: {', '.join(high_credibility[:3])}"
            )

        if low_credibility:
            recommendations.append(
                f"Consider verifying information from: {', '.join(low_credibility)}"
            )

        if not high_credibility and credibility_scores:
            recommendations.append(
                "Mixed source credibility - cross-verification recommended"
            )

        return recommendations

    def _generate_keyword_insights(
        self, keywords: Dict[str, int], clusters: Dict[str, List[str]]
    ) -> List[str]:
        """Generate insights for keyword analysis."""
        insights = []

        if keywords:
            top_keyword = max(keywords.items(), key=lambda x: x[1])[0]
            insights.append(f"Most prominent keyword: '{top_keyword}'")

        if clusters:
            insights.append(
                f"Identified {len(clusters)} keyword clusters showing related topics"
            )

        keyword_diversity = len(keywords)
        if keyword_diversity > 20:
            insights.append("High keyword diversity suggests broad topic coverage")
        elif keyword_diversity < 5:
            insights.append("Low keyword diversity indicates focused topic coverage")

        return insights

    def _generate_quality_insights(
        self, relevance_scores: List[float], quality_metrics: List[float]
    ) -> List[str]:
        """Generate insights for quality analysis."""
        insights = []

        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            if avg_relevance > 0.7:
                insights.append("High average relevance across results")
            elif avg_relevance < 0.4:
                insights.append(
                    "Low average relevance - consider refining search query"
                )

        if quality_metrics:
            avg_quality = sum(quality_metrics) / len(quality_metrics)
            if avg_quality > 0.7:
                insights.append("High content quality observed in results")
            elif avg_quality < 0.4:
                insights.append(
                    "Variable content quality - verify critical information"
                )

        return insights
