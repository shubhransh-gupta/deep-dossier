"""
Core DeepResearchAgent orchestrator leveraging Gemini for autonomous multi-step research.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import ResearchConfig
from .search import SearchEngine, SearchResult
from .crawler import WebCrawler, ScrapedDocument
from .llm import UnifiedLLM

logger = logging.getLogger(__name__)


class DeepResearchAgent:
    """
    Autonomous research agent that decomposes questions, searches the web recursively,
    crawls deep documentation/papers, and synthesizes publication-grade reports.
    Supports Gemini, OpenAI, Claude, DeepSeek, Nemotron, and Ollama.
    """

    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        self.config.validate()

        self.search_engine = SearchEngine(timeout=self.config.timeout_seconds)
        self.crawler = WebCrawler(
            user_agent=self.config.user_agent,
            timeout=self.config.timeout_seconds,
        )
        self.llm = UnifiedLLM(
            provider=self.config.provider,
            model=self.config.model,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds * 3,
        )

    def _call_llm(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Invokes the unified multi-provider LLM."""
        return self.llm.generate(prompt, system_instruction=system_instruction)

    def research(self, topic: str, on_progress=None) -> Dict[str, Any]:
        """
        Executes an end-to-end autonomous deep research workflow.
        """
        def report_step(step_msg: str):
            if on_progress:
                on_progress(step_msg)
            elif self.config.verbose:
                print(f"[*] {step_msg}")

        report_step(f"Starting deep research on: '{topic}'")

        # Phase 1: Planning and Query Decomposition
        report_step("Phase 1: Generating research plan and query decomposition...")
        initial_queries = self._generate_search_queries(topic)
        report_step(f"Generated {len(initial_queries)} research angles: {', '.join(initial_queries)}")

        all_scraped_docs: Dict[str, ScrapedDocument] = {}
        all_sources: List[Dict[str, str]] = []
        visited_urls = set()

        current_queries = initial_queries

        # Phase 2: Recursive Deep Web Crawling Loop
        for depth in range(1, self.config.max_depth + 1):
            report_step(f"Phase 2 (Depth {depth}/{self.config.max_depth}): Searching and extracting evidence...")

            new_urls = []
            for q in current_queries:
                search_results = self.search_engine.search(q, max_results=self.config.breadth)
                for res in search_results:
                    if res.url not in visited_urls and len(visited_urls) < self.config.max_sources_to_scrape:
                        visited_urls.add(res.url)
                        new_urls.append(res.url)
                        all_sources.append({"title": res.title, "url": res.url, "snippet": res.snippet})

            if not new_urls:
                report_step("No new URLs found in this pass. Proceeding to synthesis...")
                break

            report_step(f"Crawling {len(new_urls)} primary sources in parallel...")
            scraped = self.crawler.scrape_urls(new_urls)
            for doc in scraped:
                all_scraped_docs[doc.url] = doc

            total_chars = sum(d.char_count for d in all_scraped_docs.values())
            report_step(f"Aggregated {len(all_scraped_docs)} documents ({total_chars:,} characters of raw knowledge).")

            # If more depth remaining, hypothesize next missing gaps
            if depth < self.config.max_depth and len(visited_urls) < self.config.max_sources_to_scrape:
                report_step("Analyzing knowledge gaps to formulate next follow-up queries...")
                current_queries = self._generate_followup_queries(topic, list(all_scraped_docs.values()))
                report_step(f"Follow-up queries: {', '.join(current_queries)}")

        # Phase 3: Synthesis & Report Generation
        report_step("Phase 3: Synthesizing publication-grade report with citations...")
        markdown_report = self._synthesize_report(topic, list(all_scraped_docs.values()), all_sources)

        report_step("Deep research completed successfully.")

        slug = re.sub(r"[^a-zA-Z0-9_-]", "_", topic.lower())[:50].strip("_")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return {
            "topic": topic,
            "slug": slug,
            "timestamp": timestamp,
            "markdown_report": markdown_report,
            "sources": all_sources,
            "document_count": len(all_scraped_docs),
            "total_chars_analyzed": sum(d.char_count for d in all_scraped_docs.values()),
        }

    def _generate_search_queries(self, topic: str) -> List[str]:
        """Prompt Gemini to break topic down into 3-4 diverse search queries."""
        prompt = f"""
You are an expert investigative research director.
Given the research topic: "{topic}"
Formulate {self.config.max_queries_per_step} high-precision, diverse search engine queries.
Cover:
1. Core technical definition / state of the art.
2. Concrete benchmark numbers, metrics, or recent developments.
3. Critiques, limitations, controversies, or competitor comparisons.

Return ONLY a JSON list of query strings. Example:
["query 1", "query 2", "query 3"]
"""
        response = self._call_llm(prompt)
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                queries = json.loads(match.group(0))
                return [str(q).strip() for q in queries if str(q).strip()][:self.config.max_queries_per_step]
        except Exception:
            pass
        return [f"{topic} overview", f"{topic} latest benchmarks", f"{topic} challenges"]

    def _generate_followup_queries(self, topic: str, docs: List[ScrapedDocument]) -> List[str]:
        """Determine what data is still ambiguous and generate next targeted queries."""
        snippets = "\n\n".join([f"[{d.title}]: {d.text_content[:800]}" for d in docs[:5]])
        prompt = f"""
Research Topic: "{topic}"
We have collected initial documents containing the following excerpts:
{snippets}

Identify the most critical missing pieces of data, contradictions, or unanswered questions.
Generate 2 targeted search queries to resolve these specific gaps.

Return ONLY a JSON array of query strings. Example:
["specific query 1", "specific query 2"]
"""
        response = self._call_llm(prompt)
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                queries = json.loads(match.group(0))
                return [str(q).strip() for q in queries if str(q).strip()][:2]
        except Exception:
            pass
        return [f"{topic} detailed analysis", f"{topic} case studies"]

    def _synthesize_report(
        self,
        topic: str,
        docs: List[ScrapedDocument],
        sources: List[Dict[str, str]]
    ) -> str:
        """
        Synthesizes an extensive, publication-grade research report.
        Feeds the rich multi-document context to Gemini's large context window.
        """
        context_blocks = []
        for idx, doc in enumerate(docs, 1):
            context_blocks.append(
                f"--- SOURCE [{idx}] ---\n"
                f"Title: {doc.title}\n"
                f"URL: {doc.url}\n"
                f"Content:\n{doc.text_content}\n"
            )

        full_context = "\n\n".join(context_blocks)
        if len(full_context) > 200000:
            full_context = full_context[:200000] + "\n\n...[Truncated context]..."

        system_instruction = (
            "You are a world-class research scientist and principal technology analyst. "
            "Write comprehensive, rigorous, deeply technical research reports. "
            "Never use fluff, cliches, or shallow generalities. Use concrete figures, tables, and citations."
        )

        prompt = f"""
RESEARCH TOPIC: "{topic}"

BELOW IS THE VERIFIED RAW SOURCE MATERIAL CRAWLED FROM THE WEB:
{full_context}

TASK:
Write an authoritative, publication-ready research dossier addressing "{topic}".

STRUCTURE YOUR REPORT USING THE FOLLOWING SECTIONS:
1. Executive Summary (Key takeaways, core findings, bottom-line verdict)
2. Background & Context (Why this matters, historical evolution)
3. Technical Architecture & Deep Dive (Specific mechanisms, formulations, protocols)
4. Empirical Data & Comparative Analysis (Create clear Markdown tables comparing metrics, benchmarks, or approaches)
5. Critical Challenges & Limitations (What are the bottlenecks, failures, or tradeoffs?)
6. Future Trajectory & Strategic Implications (Where is this heading over the next 2-5 years?)
7. Key Takeaways & Actionable Guidance

CITATION RULES:
- Use in-text numeric citations like [1], [2], [3] whenever citing specific facts, numbers, or claims.
- At the end of the report, include a 'References' section matching the numbers to the URLs from the source material.

Ensure the report is thorough, highly informative, and reads like a premier institutional research paper.
"""
        return self._call_llm(prompt, system_instruction=system_instruction)
