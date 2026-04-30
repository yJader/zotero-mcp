---
name: zotero-paper-note-writer
description: Fill or refresh an existing Zotero Better Notes paper-reading note via zotero-mcp. Use when Codex needs to locate a paper by note key, item key, Better BibTeX citekey, or short title query, read the paper content from user-provided text or Zotero metadata/full text, generate a Chinese 3-pass reading note, and write HTML section bodies back into an existing Better Notes template without overwriting the template structure.
---

# Zotero Paper Note Writer

Fill an existing Zotero Better Notes paper note with structured 3-pass reading content. Preserve the existing note template and replace only the section bodies.

## Reference Files

Read only what you need:

- `references/better-notes-template.html`: the canonical Better Notes template. Keep it intact so later template changes only require editing this file.
- `references/analysis-prompt.md`: the canonical reading-analysis prompt. Keep it intact so later prompt changes only require editing this file.
- `references/template-map.md`: canonical section ids, target headings, merge rules, allowed HTML tags, and fallback phrasing.

## Workflow

1. Resolve the target note in this order:
   - explicit `note_key`
   - explicit `item_key`
   - Better BibTeX `citekey`
   - short title query through `zotero_search_items`
2. If the item lookup returns multiple plausible papers, stop and ask the user which item to use.
3. Retrieve child notes with `zotero_get_item_children` or `zotero_get_notes(raw_html=true)`.
4. If no note exists, stop and tell the user to create the Better Notes note manually first. Do not create a production note automatically.
5. If multiple notes exist, list the note keys and require the user to choose one. Do not guess.
6. Gather paper content:
   - If the user already pasted paper text or paper fragments, use that as the primary evidence.
   - Otherwise call `zotero_get_item_metadata`, then `zotero_get_item_fulltext` if needed.
   - If full text is truncated or semantic search is unavailable, locate the PDF attachment, extract text to `/tmp` with a local tool such as `pdftotext -layout`, and use targeted searches for methods, experiments, figures/tables, results, limitations, and conclusion.
7. Load `references/analysis-prompt.md` and preserve its contents. Append the output contract from `references/template-map.md` so the model returns section HTML by stable section id.
8. Generate section bodies in Chinese. Keep proper nouns, dataset names, metric names, and method names in English when helpful.
9. Merge the generated section bodies into the existing note with `scripts/merge_better_notes_sections.py`. A targeted refresh may include only the section ids requested by the user.
10. Validate the merged HTML before write-back: list headings with `--list-headings`, confirm required snippets are present, and confirm the note still ends with the same Zotero/Better Notes wrapper shape as the source note.
11. Before any write-back, confirm the environment supports note writes. In local-mode setups this usually means hybrid mode with `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, and `ZOTERO_LIBRARY_TYPE`; if shell environment variables are missing, also check the active MCP server configuration or use `zotero_update_note` capability as the source of truth.
12. Write the merged HTML back with `zotero_update_note`.

## Output Contract

Require the model to return exactly one JSON object keyed by the canonical section ids defined in `references/template-map.md`.

- Each value must be an HTML fragment for that section body only.
- Do not emit `<h2>` or `<h3>` tags in section bodies.
- Prefer only these tags: `<p>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<em>`, `<code>`, `<blockquote>`.
- Do not insert `<img>`, attachment markup, scripts, styles, or wrapper `<html>`/`<body>` tags.
- If information is missing, write `论文未说明` or `从当前提供的片段无法确认` exactly where needed.

## Merge Rules

- Preserve the top metadata table, styles, chapter headers, explanatory blockquotes, and the outer `<div data-schema-version="9">`.
- Preserve the note wrapper exactly as retrieved. Local DB reads may include `<div class="zotero-note znv1">` around the Better Notes schema div, while Web API reads may return only `<div data-schema-version="9">`.
- Replace only the body content under the mapped headings.
- For `h3` sections that have an explanatory `blockquote` immediately after the heading, preserve that blockquote and replace only the content after it.
- For `🎓 关键概念` and `acronyms (缩写)`, replace the content after the heading until the next `h3` or `h2`.
- Replace existing content instead of appending duplicates.
- For the final section, preserve trailing wrapper closing tags instead of replacing through the physical end of the note.
- If any required heading anchor is missing or ambiguous, stop and ask the user instead of guessing.

## Testing Rules

- Never test on the original production note.
- For write-back tests, clone the original note first, rename the first `<h1>` to start with `[TEST COPY]`, and write only to that cloned note.
- Use `zotero_create_note` only for test-note cloning. Do not use it in the normal user workflow.
- Delete successful test copies after verification unless the user wants them kept.
- If `zotero_create_note`, `zotero_update_note`, or `zotero_delete_note` fail because web credentials are missing, stop mutating the library and report that hybrid mode is required for write-path testing.

## Environment Notes

- Prefer the bundled merge script with the system Python.
- Keep transient note HTML, updates JSON, extracted PDF text, and validation artifacts under `/tmp`; do not create these files in the repository workspace unless the user asks for reusable fixtures.
- Only create `.venv` inside this skill if validation tooling or real note parsing needs extra dependencies.
- If `.venv` is created, keep third-party dependencies in `scripts/requirements.txt` and invoke the script through `.venv/bin/python`.
