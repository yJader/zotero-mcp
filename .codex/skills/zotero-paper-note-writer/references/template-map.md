# Better Notes Template Map

This file defines the stable ids used by the analysis output and the corresponding headings inside the Better Notes HTML template.

## Section Ids

Use these keys in the analysis JSON output:

```json
{
  "category": "<p>...</p>",
  "core_problem": "<p>...</p>",
  "main_contribution": "<ul><li>...</li></ul>",
  "structure": "<p>...</p>",
  "key_concepts": "<ul><li>...</li></ul>",
  "acronyms": "<ul><li>...</li></ul>",
  "method_system_design": "<p>...</p>",
  "experiment_setup": "<ul><li>...</li></ul>",
  "key_figures_tables": "<ul><li>...</li></ul>",
  "main_results": "<ul><li>...</li></ul>",
  "questions": "<ul><li>...</li></ul>",
  "strengths": "<ul><li>...</li></ul>",
  "weaknesses": "<ul><li>...</li></ul>",
  "future_work": "<ul><li>...</li></ul>",
  "connection": "<ul><li>...</li></ul>",
  "insights": "<ul><li>...</li></ul>"
}
```

## Heading Mapping

| Section id | Target heading text |
| --- | --- |
| `category` | `1. 论文类别 (Category)` |
| `core_problem` | `2. 核心问题 (Core Problem)` |
| `main_contribution` | `3. 主要贡献 (Main Contribution)` |
| `structure` | `4. 论文结构 (Structure)` |
| `key_concepts` | `🎓 关键概念` |
| `acronyms` | `acronyms (缩写)` |
| `method_system_design` | `1. 方法 / 模型 / 系统设计 (Method / Model / System Design)` |
| `experiment_setup` | `2. 实验设置 (Experiment Setup)` |
| `key_figures_tables` | `3. 关键图表分析 (Key Figures/Tables Analysis)` |
| `main_results` | `4. 主要结果 (Main Results)` |
| `questions` | `5. 疑问点 (Questions)` |
| `strengths` | `1. 优点 / 创新点 (Strengths / Innovations)` |
| `weaknesses` | `2. 缺点 / 局限性 (Weaknesses / Limitations)` |
| `future_work` | `3. 可改进点 / 未来工作 (Future Work)` |
| `connection` | `4. 相关工作联系 (Connection to Related Work)` |
| `insights` | `5. 个人思考 / 启发 (My Thoughts / Inspiration)` |

## Merge Behavior

- Preserve every existing heading and the explanatory `blockquote` that immediately follows the `h3` title when present.
- Replace only the body content between that preserved header area and the next `h2` or `h3`.
- Treat `🎓 关键概念` and `acronyms (缩写)` exactly like the other body sections even though they usually have no explanatory blockquote.
- Do not touch the top metadata table.
- Do not add new headings.
- Do not append a second copy of an existing section body.

## Missing Information Policy

- If the paper does not specify a fact, write `论文未说明`.
- If the current user-provided excerpt is insufficient to confirm a fact, write `从当前提供的片段无法确认`.
- Prefer explicit uncertainty over guesswork.

## Allowed HTML

Preferred tags:

- `<p>`
- `<ul>`
- `<ol>`
- `<li>`
- `<strong>`
- `<em>`
- `<code>`
- `<blockquote>`

Avoid:

- `<h1>` to `<h6>`
- `<table>`
- `<img>`
- inline styles
- scripts
- wrapper tags such as `<html>` or `<body>`

## Notes

- `前置背景` does not have its own target heading in the current template. Merge that content into `key_concepts`.
- The merge script matches headings by normalized visible text, not by exact raw HTML.
