#!/usr/bin/env python3
"""Merge generated HTML section bodies into a Better Notes paper template."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


SECTION_TO_HEADING = {
    "category": "1. 论文类别 (Category)",
    "core_problem": "2. 核心问题 (Core Problem)",
    "main_contribution": "3. 主要贡献 (Main Contribution)",
    "structure": "4. 论文结构 (Structure)",
    "key_concepts": "🎓 关键概念",
    "acronyms": "acronyms (缩写)",
    "method_system_design": "1. 方法 / 模型 / 系统设计 (Method / Model / System Design)",
    "experiment_setup": "2. 实验设置 (Experiment Setup)",
    "key_figures_tables": "3. 关键图表分析 (Key Figures/Tables Analysis)",
    "main_results": "4. 主要结果 (Main Results)",
    "questions": "5. 疑问点 (Questions)",
    "strengths": "1. 优点 / 创新点 (Strengths / Innovations)",
    "weaknesses": "2. 缺点 / 局限性 (Weaknesses / Limitations)",
    "future_work": "3. 可改进点 / 未来工作 (Future Work)",
    "connection": "4. 相关工作联系 (Connection to Related Work)",
    "insights": "5. 个人思考 / 启发 (My Thoughts / Inspiration)",
}

TAG_RE = re.compile(r"(?is)<[^>]+>")
HEADING_RE = re.compile(r"(?is)<h(?P<level>[23])\b[^>]*>.*?</h(?P=level)>")
BLOCKQUOTE_PREFIX_RE = re.compile(r"(?is)^(?P<ws>\s*)(?P<tag><blockquote\b.*?</blockquote>)")
H1_RE = re.compile(r"(?is)<h1\b(?P<attrs>[^>]*)>(?P<body>.*?)</h1>")
TRAILING_DIVS_RE = re.compile(r"(?is)\s*(?:</div>\s*)+$")


def normalize_visible_text(text: str) -> str:
    text = html.unescape(text)
    text = TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def heading_matches(actual: str, expected: str) -> bool:
    return normalize_visible_text(actual) == normalize_visible_text(expected)


def split_headings(note_html: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for match in HEADING_RE.finditer(note_html):
        headings.append(
            {
                "level": int(match.group("level")),
                "start": match.start(),
                "end": match.end(),
                "raw": match.group(0),
                "text": normalize_visible_text(match.group(0)),
            }
        )
    return headings


def find_heading_index(headings: list[dict[str, Any]], expected_text: str) -> int:
    matches = [i for i, heading in enumerate(headings) if heading_matches(heading["raw"], expected_text)]
    if not matches:
        raise ValueError(f"Missing heading anchor: {expected_text}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous heading anchor: {expected_text}")
    return matches[0]


def content_start_after_preserved_blockquote(note_html: str, heading_end: int) -> int:
    remainder = note_html[heading_end:]
    match = BLOCKQUOTE_PREFIX_RE.match(remainder)
    if not match:
        return heading_end
    return heading_end + match.end()


def content_end_before_trailing_wrappers(note_html: str, content_start: int) -> int:
    """Preserve Zotero/Better Notes wrapper closing tags after the final section."""
    match = TRAILING_DIVS_RE.search(note_html)
    if not match:
        return len(note_html)
    if match.start() <= content_start:
        return len(note_html)
    return match.start()


def compute_replacements(note_html: str, updates: dict[str, str]) -> list[tuple[int, int, str]]:
    headings = split_headings(note_html)
    replacements: list[tuple[int, int, str]] = []
    for section_id, new_html in updates.items():
        if section_id not in SECTION_TO_HEADING:
            raise ValueError(f"Unknown section id: {section_id}")
        heading_index = find_heading_index(headings, SECTION_TO_HEADING[section_id])
        heading = headings[heading_index]
        start = content_start_after_preserved_blockquote(note_html, heading["end"])
        end = (
            headings[heading_index + 1]["start"]
            if heading_index + 1 < len(headings)
            else content_end_before_trailing_wrappers(note_html, start)
        )
        replacement = "\n" + new_html.strip() + "\n"
        replacements.append((start, end, replacement))
    replacements.sort(key=lambda item: item[0])
    for left, right in zip(replacements, replacements[1:]):
        if left[1] > right[0]:
            raise ValueError("Overlapping section replacements detected")
    return replacements


def apply_replacements(note_html: str, replacements: list[tuple[int, int, str]]) -> str:
    parts: list[str] = []
    cursor = 0
    for start, end, replacement in replacements:
        parts.append(note_html[cursor:start])
        parts.append(replacement)
        cursor = end
    parts.append(note_html[cursor:])
    return "".join(parts)


def rename_first_h1(note_html: str, prefix: str) -> str:
    match = H1_RE.search(note_html)
    if not match:
        raise ValueError("Missing first <h1> in note HTML")

    body = match.group("body")
    text = normalize_visible_text(body)
    if text.startswith(prefix):
        return note_html

    text_match = re.search(re.escape(text), body)
    if text_match:
        start, end = text_match.span()
        new_body = body[:start] + prefix + " " + body[start:end] + body[end:]
    else:
        new_body = prefix + " " + body

    return note_html[: match.start()] + f"<h1{match.group('attrs')}>{new_body}</h1>" + note_html[match.end() :]


def load_updates(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Updates JSON must be an object")
    normalized: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(value, str):
            raise ValueError(f"Section '{key}' must map to an HTML string")
        normalized[str(key)] = value
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-html", required=True, help="Path to the existing note HTML file")
    parser.add_argument("--updates-json", help="Path to a JSON file keyed by canonical section ids")
    parser.add_argument("--output-html", help="Write merged HTML to this file instead of stdout")
    parser.add_argument("--rename-h1-prefix", help="Prefix the first visible H1 text with this marker")
    parser.add_argument("--list-headings", action="store_true", help="Print normalized H2/H3 headings and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_html)
    note_html = input_path.read_text()

    if args.list_headings:
        for heading in split_headings(note_html):
            print(f"h{heading['level']}: {heading['text']}")
        return 0

    if args.rename_h1_prefix:
        note_html = rename_first_h1(note_html, args.rename_h1_prefix)

    if args.updates_json:
        updates = load_updates(Path(args.updates_json))
        note_html = apply_replacements(note_html, compute_replacements(note_html, updates))

    if args.output_html:
        Path(args.output_html).write_text(note_html)
    else:
        sys.stdout.write(note_html)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
