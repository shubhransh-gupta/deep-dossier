"""
Web crawler and content extractor for deep document analysis.
"""

import re
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ScrapedDocument:
    url: str
    title: str
    text_content: str
    char_count: int
    success: bool
    error: Optional[str] = None


class WebCrawler:
    """Extracts clean article content from URLs in parallel."""

    def __init__(self, user_agent: str, timeout: int = 15, max_workers: int = 5):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def scrape_url(self, url: str) -> ScrapedDocument:
        """Fetch and extract readable text from a single webpage."""
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()

            # Check content type
            content_type = resp.headers.get("Content-Type", "").lower()
            if "pdf" in content_type or url.lower().endswith(".pdf"):
                return self._extract_pdf(resp.content, url)

            return self._extract_html(resp.text, url)
        except Exception as e:
            logger.debug(f"Failed to crawl {url}: {e}")
            return ScrapedDocument(
                url=url,
                title="",
                text_content="",
                char_count=0,
                success=False,
                error=str(e),
            )

    def scrape_urls(self, urls: List[str]) -> List[ScrapedDocument]:
        """Crawl multiple URLs concurrently."""
        results: List[ScrapedDocument] = []
        unique_urls = list(dict.fromkeys(urls))  # Preserve order, deduplicate

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_url, u): u for u in unique_urls}
            for future in as_completed(future_to_url):
                res = future.result()
                if res.success and res.char_count > 100:
                    results.append(res)
        return results

    def _extract_html(self, html: str, url: str) -> ScrapedDocument:
        """Parse HTML, eliminate clutter, and extract dense readable text."""
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Remove clutter
        for unwanted in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "aside"]):
            unwanted.decompose()

        # Target main content containers if present
        main_content = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", {"id": re.compile(r"(content|main|article)", re.I)})
            or soup.find("div", {"class": re.compile(r"(content|main|article|post)", re.I)})
            or soup.body
        )

        if not main_content:
            text = soup.get_text(separator="\n", strip=True)
        else:
            text = main_content.get_text(separator="\n", strip=True)

        # Normalize extra blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n\n".join(lines)

        # Cap text length to avoid token explosion (e.g. 50,000 characters per document)
        if len(cleaned_text) > 60000:
            cleaned_text = cleaned_text[:60000] + "\n...[truncated for length]..."

        return ScrapedDocument(
            url=url,
            title=title or url,
            text_content=cleaned_text,
            char_count=len(cleaned_text),
            success=True,
        )

    def _extract_pdf(self, content: bytes, url: str) -> ScrapedDocument:
        """Extract text from PDF if pypdf or PyPDF2 is available, otherwise basic raw fallback."""
        try:
            import io
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages[:20]:  # First 20 pages max
                text += page.extract_text() + "\n"
            return ScrapedDocument(
                url=url,
                title=f"PDF Document: {url.split('/')[-1]}",
                text_content=text.strip(),
                char_count=len(text),
                success=True,
            )
        except Exception:
            return ScrapedDocument(
                url=url,
                title=f"PDF: {url.split('/')[-1]}",
                text_content="[Binary PDF content could not be parsed without pypdf]",
                char_count=0,
                success=False,
                error="pypdf not installed",
            )
