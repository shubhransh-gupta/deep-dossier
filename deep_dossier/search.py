"""
Search module providing search capabilities via DuckDuckGo and custom search backends.
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"


class SearchEngine:
    """Multi-backend search engine supporting DuckDuckGo and fallback methods."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform search with retries and fallback."""
        results: List[SearchResult] = []
        try:
            results = self._search_duckduckgo(query, max_results)
            if results:
                return results
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed for '{query}': {e}")

        # Fallback search if DDG failed
        try:
            results = self._search_html_fallback(query, max_results)
        except Exception as e:
            logger.error(f"Fallback search also failed for '{query}': {e}")

        return results

    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using duckduckgo_search library."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))
                results = []
                for r in raw_results:
                    title = r.get("title", "")
                    url = r.get("href", "")
                    body = r.get("body", "")
                    if url and (title or body):
                        results.append(SearchResult(title=title, url=url, snippet=body))
                return results
        except Exception as e:
            logger.debug(f"DDGS error: {e}")
            raise

    def _search_html_fallback(self, query: str, max_results: int) -> List[SearchResult]:
        """Direct lightweight HTTP fallback for DuckDuckGo HTML endpoint."""
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse

        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.post(
            url,
            data={"q": query},
            headers=headers,
            timeout=self.timeout
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result", limit=max_results):
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            if title_tag:
                raw_link = title_tag.get("href", "")
                parsed_link = urllib.parse.parse_qs(urllib.parse.urlparse(raw_link).query).get("uddg")
                clean_url = parsed_link[0] if parsed_link else raw_link
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                if clean_url.startswith("http"):
                    results.append(SearchResult(title=title, url=clean_url, snippet=snippet, source="ddg-html"))
        return results
