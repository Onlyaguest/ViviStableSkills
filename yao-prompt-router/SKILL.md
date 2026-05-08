---
name: yao-prompt-router
description: Smart router for 102 Chinese AI prompt templates from yao-open-prompts.
version: 1.0.0
author: Vivi
tags: [prompts, ai-agents, content-creation, marketing, geo]
platforms: [all]
dependencies: []
---

# Yao Prompt Router

102 Chinese AI prompt templates, one natural-language entry point. Say what you need, get the right template.

## Features

- Natural language intent matching across 9 categories (102 templates)
- Installed-skill priority routing (17 known skills checked first)
- Auto variable detection and guided fill-in
- Full prompt execution after matching

## Quick Start

```bash
# Install prompt files
./install.sh

# Then in Claude Code, just say:
# "Help me write a Xiaohongshu post"   -> matches Xiaohongshu Expert
# "Optimize this title"                -> matches Title Optimizer
# "Make a GEO strategy"                -> matches GEO series
```

## Execution Flow

When triggered, follow these steps exactly:

### Step 1: Understand Intent

Extract from user's natural language:
- **Task type**: write / analyze / generate / optimize / research
- **Platform**: WeChat / Xiaohongshu / Douyin / Bilibili / web
- **Industry**: food / fitness / travel / tech / education / medical
- **Specific need**: title / script / contract / PPT / GEO

### Step 2: Check Installed Skills (Priority)

Before matching prompt templates, check if a more capable installed skill exists:

| Intent | Check Skill | When to use |
|---|---|---|
| PPT / slides | `any2deck` | Full slide generation |
| WeChat long article | `khazix-writer` | Complete writing system |
| Style cloning | `style-clone` | Professional style extraction |
| Anti-AI detection | `anti-wechat-ai-check` | WeChat compliance |
| Contract review | `contract-review-pro` | Professional review |
| Deep research | `hv-analysis` | 10k-word analysis |
| Frontend / landing page | `frontend-design` | Production-grade UI |
| Form filling | `fill-form` | Auto form detection |
| Expense report | `expense-report` | Invoice to Excel |
| Image generation | `image-creator` | Multi-engine output |
| Book writing | `write-professional-book` | Multi-chapter books |
| Thesis polish | `thesis-polish` | National-level quality |
| Translation review | `translation-review` | 6-dimension review |
| Business proposal | `proposal` | Proposal + quote |
| Event planning | `event-curator` | Complete event plan |

If matched, inform user: "Detected `{skill}` is installed, it handles this better. Use it?"

### Step 3: Match Prompt Template

From `prompt-index.json` or the catalog in `docs/prompt-catalog.md`, match 1-3 best templates.

**Priority rules:**
1. Exact tag hit (user keywords match template tags)
2. Subcategory match
3. Semantic similarity

**Category quick match:**
- User mentions "prompt engineering" -> AI Methods (8 templates)
- User mentions specific industry -> Industry Expert (13 templates)
- User mentions platform name -> Platform Operations (5 templates)
- User mentions GEO/SEO/AI search -> GEO Marketing (28 templates)
- User mentions writing/copywriting -> Content Creation (46 templates)
- Default for prompt generation -> Meta Prompt System V0.6

### Step 4: Read and Execute

1. Read the matched `.md` file from `~/.claude/skills/yao-*/`
2. Locate the `## Prompt` section
3. Check for `{{variables}}` or `[placeholders]` -> ask user to fill
4. Execute as the role defined in the prompt

## Output Format

```
Matched: "{title}"
Category: {category}/{subcategory}
Source: {file_path}

[If installed skill available, note here]

Loading template...
---
[Execute as the prompt's role]
```

## Categories Overview

| # | Category | Count | Key scenarios |
|---|---|---|---|
| 1 | AI Methods | 8 | Meta prompts, reverse engineering |
| 2 | AI Work | 10 | Research, contracts, PPT, landing pages |
| 3 | AI Learning | 3 | Keywords, memory, habits |
| 4 | AI Life | 2 | Health report, parent-child songs |
| 5 | AI Education | 1 | Children's interactive learning |
| 6 | AI Content | 46 | Copywriting, platforms, industries |
| 7 | AI Coding | 1 | System architecture |
| 8 | AI Marketing | 28 | GEO full pipeline |
| 9 | AI Thinking | 3 | Memory palace, self-critique |

Full catalog: [docs/prompt-catalog.md](docs/prompt-catalog.md)

## Installation

See `install.sh` or [README.md](README.md).

## Troubleshooting

**Template not found?** Ensure yao-open-prompts is installed: `ls ~/.claude/skills/yao-*/`

**Wrong match?** Tell the router what you need more specifically. It re-matches on clarification.

**Skill conflict?** Router always asks before redirecting to an installed skill. You can choose the prompt template instead.
