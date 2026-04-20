#!/usr/bin/env python3
"""
Generate index.html for briefing-archive.

Scans ai/, energy-chem/, world/ for YYYY-MM-DD.html files and builds a
category-card landing page. No external deps — pure stdlib.

Usage:
    python3 generate_index.py [--archive-root PATH]

Exits 0 on success. Idempotent — safe to run any time.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.html$")

CATEGORIES = [
    # (folder, display_name, emoji, description, accent_hex)
    ("ai", "AI", "AI", "GPT · Gemini · Claude · Meta · xAI · Mistral 최신 업데이트", "#b34700"),
    ("energy-chem", "Energy & Chem", "EC", "에너지·화학공학 논문·정책·산업·프리프린트", "#1d6b4f"),
    ("world", "World", "WD", "전세계 시사·정치·경제·문화 뉴스", "#2a4b8d"),
]


@dataclass
class Entry:
    date: str  # YYYY-MM-DD
    href: str  # relative path
    title: str


def scan_category(archive_root: Path, folder: str) -> list[Entry]:
    dir_path = archive_root / folder
    if not dir_path.is_dir():
        return []
    entries: list[Entry] = []
    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        m = DATE_RE.match(f.name)
        if not m:
            continue
        date = m.group(1)
        entries.append(
            Entry(date=date, href=f"{folder}/{f.name}", title=date)
        )
    entries.sort(key=lambda e: e.date, reverse=True)
    return entries


def build_html(data: dict[str, list[Entry]]) -> str:
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    total = sum(len(v) for v in data.values())

    cards = []
    for folder, name, emoji, desc, accent in CATEGORIES:
        entries = data.get(folder, [])
        # show latest 15 per category
        visible = entries[:15]
        extra = len(entries) - len(visible)

        links_html = "\n".join(
            f'          <li><a href="{html.escape(e.href)}"><time>{html.escape(e.date)}</time></a></li>'
            for e in visible
        ) or '          <li class="empty">아직 브리핑이 없습니다.</li>'

        more_html = (
            f'        <p class="more">외 {extra}건</p>' if extra > 0 else ""
        )

        cards.append(f"""      <article class="card" style="--accent: {accent}">
        <header class="card-head">
          <span class="tag">{html.escape(emoji)}</span>
          <h2>{html.escape(name)}</h2>
          <p class="desc">{html.escape(desc)}</p>
          <p class="count">{len(entries)}건</p>
        </header>
        <ul class="list">
{links_html}
        </ul>
{more_html}
      </article>""")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Briefing Archive</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Noto+Serif+KR:wght@700;900&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: #fafaf7;
    color: #1a1a1a;
    font-family: 'Noto Sans KR', sans-serif;
    font-weight: 400;
    line-height: 1.6;
  }}
  .page {{ max-width: 1100px; margin: 0 auto; padding: 40px 24px 80px; }}

  .masthead {{
    border-top: 3px double #1a1a1a;
    border-bottom: 3px double #1a1a1a;
    padding: 28px 0 22px;
    text-align: center;
    margin-bottom: 40px;
  }}
  .masthead h1 {{
    font-family: 'Playfair Display', 'Noto Serif KR', serif;
    font-weight: 900;
    font-size: 48px;
    letter-spacing: 6px;
    margin: 0;
  }}
  .masthead .dateline {{
    font-size: 13px; letter-spacing: 2px; text-transform: uppercase;
    color: #555; margin-top: 12px;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }}

  .card {{
    background: #fff;
    border: 1px solid #e5e2dc;
    border-top: 4px solid var(--accent);
    padding: 24px 24px 20px;
    display: flex; flex-direction: column;
  }}
  .card-head .tag {{
    display: inline-block;
    font-family: 'Playfair Display', serif;
    font-weight: 900;
    font-size: 12px; letter-spacing: 2px;
    color: #fff; background: var(--accent);
    padding: 3px 10px; border-radius: 2px;
  }}
  .card-head h2 {{
    font-family: 'Playfair Display', 'Noto Serif KR', serif;
    font-weight: 900;
    font-size: 26px;
    margin: 12px 0 4px;
    color: #1a1a1a;
  }}
  .card-head .desc {{
    font-size: 13px; color: #555; margin: 0 0 14px;
  }}
  .card-head .count {{
    font-size: 11px; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--accent);
    font-weight: 700; margin: 0 0 14px;
  }}

  .list {{
    list-style: none; padding: 0; margin: 0;
    border-top: 1px solid #ececec;
  }}
  .list li {{
    border-bottom: 1px solid #f1f1f1;
  }}
  .list li.empty {{
    padding: 14px 0; color: #999; font-size: 13px; font-style: italic;
  }}
  .list a {{
    display: block;
    padding: 11px 0;
    color: #1a1a1a;
    text-decoration: none;
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 14px;
  }}
  .list a:hover {{
    color: var(--accent);
    padding-left: 6px;
    transition: padding-left 0.15s, color 0.15s;
  }}
  .list time {{ font-variant-numeric: tabular-nums; }}

  .more {{
    font-size: 12px; color: #888;
    margin: 10px 0 0; text-align: right; font-style: italic;
  }}

  footer {{
    margin-top: 60px; padding-top: 20px;
    border-top: 1px solid #e5e2dc;
    text-align: center;
    font-size: 12px; color: #888;
  }}
  footer code {{
    background: #f0ede7; padding: 2px 6px; border-radius: 2px;
    font-size: 11px;
  }}

  @media (max-width: 600px) {{
    .masthead h1 {{ font-size: 32px; letter-spacing: 3px; }}
    .page {{ padding: 24px 16px 60px; }}
  }}
</style>
</head>
<body>
  <div class="page">
    <header class="masthead">
      <h1>BRIEFING ARCHIVE</h1>
      <p class="dateline">Auto-generated · {html.escape(gen_time)} · Total {total} entries</p>
    </header>

    <main class="grid">
{chr(10).join(cards)}
    </main>

    <footer>
      Generated by <code>scripts/generate_index.py</code> · Deployed via GitHub Pages
    </footer>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Archive root directory (default: repo root)",
    )
    args = parser.parse_args()
    root = Path(args.archive_root).resolve()

    if not root.is_dir():
        print(f"ERROR: archive root not found: {root}", file=sys.stderr)
        return 1

    data: dict[str, list[Entry]] = {}
    for folder, *_ in CATEGORIES:
        data[folder] = scan_category(root, folder)

    html_out = build_html(data)
    (root / "index.html").write_text(html_out, encoding="utf-8")

    total = sum(len(v) for v in data.values())
    per_cat = ", ".join(f"{name}={len(data[f])}" for f, name, *_ in CATEGORIES)
    print(f"OK: index.html generated ({total} total: {per_cat})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
