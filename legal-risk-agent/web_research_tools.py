# web_research_tools.py
import os
from typing import Literal
from tavily import TavilyClient

class WebResearcher:
    """
    Provides web search and content retrieval capabilities for legal research.

    This class wraps the Tavily API to provide targeted web search capabilities.
    Tavily is particularly good for this use case because it returns structured
    results with content summaries, which is more useful than raw HTML.
    """

    def __init__(self, api_key: str):
        """Initialize the web researcher with Tavily API credentials."""
        self.client = TavilyClient(api_key=api_key)

    def search(
        self,
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news"] = "general",
        include_raw_content: bool = False
    ) -> str:
        """
        Perform a web search for legal information.

        Args:
            query: The search query (be specific for best results)
            max_results: Number of results to return (default 5)
            topic: Search category - "general" for regulations/case law,
                   "news" for recent developments
            include_raw_content: Whether to include full page content (token-intensive)

        Returns:
            Formatted search results with titles, URLs, and summaries
        """
        try:
            results = self.client.search(
                query=query,
                max_results=max_results,
                topic=topic,
                include_raw_content=include_raw_content
            )

            # Format results in a structured way that's easy for agents to parse
            formatted_results = []
            formatted_results.append(f"Search Query: {query}\n")
            formatted_results.append(f"Found {len(results.get('results', []))} results:\n")

            for idx, result in enumerate(results.get('results', []), 1):
                formatted_results.append(f"\n--- Result {idx} ---")
                formatted_results.append(f"Title: {result.get('title', 'N/A')}")
                formatted_results.append(f"URL: {result.get('url', 'N/A')}")
                formatted_results.append(f"Summary: {result.get('content', 'N/A')}")

                if include_raw_content and 'raw_content' in result:
                    # Truncate raw content to prevent token explosion
                    raw = result['raw_content'][:2000]
                    formatted_results.append(f"Content Preview: {raw}...")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Web search error: {str(e)}\nPlease try a different query or check your API connection."

def create_web_research_tools(api_key: str):
    """
    Factory function to create web research tool instances.

    Args:
        api_key: Tavily API key

    Returns:
        Tuple of (internet_search, web_fetch) tool functions
    """
    researcher = WebResearcher(api_key)

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news"] = "general"
    ) -> str:
        """
        Search the web for legal information, case law, or regulatory guidance.

        Use this tool to find external context about legal issues identified in
        documents. Formulate specific queries for best results.

        Args:
            query: Specific search query (e.g., "GDPR Article 82 damages calculation")
            max_results: Number of results to return (1-10, default 5)
            topic: "general" for legal research, "news" for recent developments

        Returns:
            Formatted search results with titles, URLs, and content summaries

        Example:
            internet_search("CCPA private right of action requirements", max_results=3)
        """
        return researcher.search(query, max_results, topic, include_raw_content=False)

    def web_fetch(url: str) -> str:
        """
        Fetch the full content of a specific web page.

        Use this after internet_search when you need complete text from a specific
        source (like a regulation or case law). This consumes more tokens but provides
        comprehensive content.

        Args:
            url: The complete URL to fetch

        Returns:
            The full text content of the page

        Note: This is token-intensive. Use selectively for key sources.
        """
        # For now, we'll use Tavily's extract functionality
        # In production, you might want a dedicated web scraping solution
        try:
            result = researcher.client.extract(url)
            return result.get('raw_content', 'Content could not be extracted from this URL.')
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

    return internet_search, web_fetch
