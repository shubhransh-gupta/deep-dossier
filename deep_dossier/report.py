"""
Report generators for Markdown, interactive HTML, and JSON dossiers.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def save_reports(data: Dict[str, Any], output_dir: Path, slug: str) -> Dict[str, Path]:
    """Saves report in Markdown, HTML, and JSON formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    # 1. Save Markdown
    md_path = output_dir / f"{slug}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(data["markdown_report"])
    paths["markdown"] = md_path

    # 2. Save JSON Dossier
    json_path = output_dir / f"{slug}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    paths["json"] = json_path

    # 3. Save Interactive HTML
    html_content = generate_html_report(data)
    html_path = output_dir / f"{slug}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    paths["html"] = html_path

    return paths


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generates an executive-grade HTML report with modern dark theme and responsive typography."""
    title = data.get("topic", "Research Report")
    timestamp = data.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    sources: List[Dict[str, str]] = data.get("sources", [])
    markdown_content = data.get("markdown_report", "")

    # Basic markdown to html conversion or simple rendering
    try:
        import markdown
        rendered_body = markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code", "toc"]
        )
    except Exception:
        # Fallback rendering if markdown package is missing
        rendered_body = (
            markdown_content
            .replace("\n\n", "</p><p>")
            .replace("# ", "<h1>")
            .replace("## ", "<h2>")
            .replace("### ", "<h3>")
        )

    sources_html = ""
    for idx, s in enumerate(sources, 1):
        url = s.get("url", "#")
        stitle = s.get("title", url)
        sources_html += f"""
        <div class="source-card">
            <span class="source-num">[{idx}]</span>
            <div class="source-info">
                <a href="{url}" target="_blank" rel="noopener noreferrer" class="source-title">{stitle}</a>
                <span class="source-url">{url}</span>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Deep Research Dossier</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111726;
            --surface-border: #1e293b;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.15);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent: #818cf8;
            --success: #34d399;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.7;
            padding: 2.5rem 1.5rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 2rem;
            margin-bottom: 2.5rem;
        }}
        .badge {{
            display: inline-block;
            background: var(--primary-glow);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            margin-bottom: 1rem;
        }}
        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.25;
            color: #ffffff;
            margin-bottom: 0.75rem;
        }}
        .meta {{
            color: var(--text-muted);
            font-size: 0.875rem;
            display: flex;
            gap: 1.5rem;
        }}
        .content {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 1rem;
            padding: 2.5rem;
            margin-bottom: 3rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }}
        .content h2 {{
            color: #ffffff;
            font-size: 1.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 0.5rem;
        }}
        .content h3 {{
            color: var(--primary);
            font-size: 1.2rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }}
        .content p {{
            margin-bottom: 1.25rem;
            color: #cbd5e1;
            font-size: 1rem;
        }}
        .content ul, .content ol {{
            margin-left: 1.5rem;
            margin-bottom: 1.25rem;
            color: #cbd5e1;
        }}
        .content li {{ margin-bottom: 0.5rem; }}
        .content blockquote {{
            border-left: 4px solid var(--primary);
            padding-left: 1rem;
            margin: 1.5rem 0;
            color: var(--text-muted);
            font-style: italic;
        }}
        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        .content th, .content td {{
            padding: 0.75rem 1rem;
            border: 1px solid var(--surface-border);
            text-align: left;
        }}
        .content th {{ background: #1e293b; color: #ffffff; }}
        code {{
            font-family: 'JetBrains Mono', monospace;
            background: #1e293b;
            color: #38bdf8;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .sources-section {{
            margin-top: 2rem;
        }}
        .source-card {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 0.5rem;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            transition: border-color 0.2s ease;
        }}
        .source-card:hover {{
            border-color: var(--primary);
        }}
        .source-num {{
            color: var(--primary);
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}
        .source-title {{
            color: #ffffff;
            font-weight: 500;
            text-decoration: none;
            display: block;
            margin-bottom: 0.25rem;
        }}
        .source-title:hover {{
            text-decoration: underline;
            color: var(--primary);
        }}
        .source-url {{
            color: var(--text-muted);
            font-size: 0.8rem;
            word-break: break-all;
        }}
        footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 3rem;
            border-top: 1px solid var(--surface-border);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="badge">Open Deep Research &bull; Gemini Autonomous Agent</span>
            <h1>{title}</h1>
            <div class="meta">
                <span>Generated: {timestamp}</span>
                <span>Sources verified: {len(sources)}</span>
            </div>
        </header>

        <main class="content">
            {rendered_body}
        </main>

        <section class="sources-section">
            <h2>Verified Citations & Bibliography ({len(sources)})</h2>
            {sources_html}
        </section>

        <footer>
            Generated by <a href="https://github.com/shubhransh-gupta/open-deep-research" style="color:var(--primary);text-decoration:none;">Open Deep Research</a> &bull; Powered by Google Gemini
        </footer>
    </div>
</body>
</html>
"""
    return html
