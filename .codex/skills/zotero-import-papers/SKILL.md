---
name: zotero-import-papers
description: >
  Batch import papers into Zotero from URLs (arXiv, conference PDFs, DOIs).
  Downloads PDFs locally and places them in Zotero local storage for WebDAV sync.
  Use when the user provides paper titles/URLs and wants them added to Zotero,
  optionally into a specific collection or new subcollection.
---

# Zotero Import Papers

Batch import papers into Zotero with PDF attachments stored locally for WebDAV sync.

## Input

The user provides:
- One or more papers, each with a **title** and a **URL** (arXiv, DOI, conference PDF, etc.)
- Optionally a **target collection** name (existing or new subcollection to create)

## Workflow

### Step 1: Parse Input

Extract from the user's message:
- A list of `(title, url)` pairs
- Target collection info: parent collection name, optional new subcollection name
- If the user says something like "在 X 中添加一个子分类 Y", that means create subcollection Y under parent X

### Step 2: Prepare Collection

1. If the user specifies a target collection, use `zotero_search_collections` to find it by name.
2. If the user wants a new subcollection:
   - Find the parent collection key first
   - Create the subcollection with `zotero_create_collection(name, parent_collection=parent_key)`
3. Record the target collection key for later use.

### Step 3: Import Metadata

For each paper, import metadata into Zotero using `zotero_add_by_url`:

- **arXiv URLs** (`arxiv.org/abs/...`): Pass directly. Metadata is auto-extracted from arXiv API.
- **DOI URLs** (`doi.org/...`): Pass directly.
- **Direct PDF URLs** (e.g., conference proceedings): Pass directly. If the result is a bare "webpage" item, use `zotero_update_item` to set the correct title and date.

Always pass `collections=[<collection_key>]` to place items in the target collection.

**Rate limiting**: arXiv API may rate-limit. If you get a timeout or rate-limit error, wait 5 seconds and retry (up to 2 retries per paper). Do NOT retry more than twice.

**Parallelism**: Call `zotero_add_by_url` for all papers in parallel. Retry failed ones sequentially.

Record each paper's `item_key` from the response.

### Step 4: Download PDFs

Download all PDFs to `/tmp/zotero-pdfs/` using `curl -L`:

- **arXiv**: Convert `arxiv.org/abs/<id>` to `arxiv.org/pdf/<id>`
- **Direct PDF URLs**: Use as-is
- **DOI URLs**: Try to resolve, or skip PDF download if not a direct PDF link

Run downloads in parallel using background `&` in a single Bash command. Verify each file exists and has non-zero size.

### Step 5: Place PDFs in Local Storage

For each imported paper:

1. Call `zotero_get_item_children(item_key)` to find the attachment entry.
2. If an attachment exists (the API typically creates one even when upload fails):
   - Get the attachment `key` and `filename`
   - Create the storage directory: `mkdir -p ~/Zotero/storage/<attachment_key>/`
   - Copy the PDF: `cp /tmp/zotero-pdfs/<file> ~/Zotero/storage/<attachment_key>/<filename>`
3. If no attachment exists:
   - Report to the user that this paper needs manual PDF attachment in Zotero

Call `zotero_get_items_children` (batch version) for all items at once to minimize API calls.

### Step 6: Verify and Report

Present a summary table:

| Paper | Item Key | PDF Status |
|-------|----------|------------|
| Title | KEY      | OK / Failed (reason) |

If any PDFs failed, list the downloaded files in `/tmp/zotero-pdfs/` so the user can attach them manually.

## Important Notes

- **Never upload PDFs via Zotero API** — the user uses WebDAV for file sync, not Zotero cloud storage.
- **Zotero storage path**: `~/Zotero/storage/<attachment_key>/<filename>` — this is the standard Zotero local storage layout.
- **Clean up**: Do NOT delete `/tmp/zotero-pdfs/` after import — keep as backup until user confirms.
- **Duplicates**: If a paper already exists in Zotero (check by title via `zotero_search_items` before importing), ask the user whether to skip or re-import.
- **arXiv metadata**: `zotero_add_by_url` for arXiv links returns rich metadata (authors, abstract, date). Prefer this over `zotero_add_from_file`.
