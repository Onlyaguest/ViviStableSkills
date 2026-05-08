# Yao Prompt Router

Smart router for 102 Chinese AI prompt templates. Say what you need, get the right template.

Source: [yaojingang/yao-open-prompts](https://github.com/yaojingang/yao-open-prompts)

## Install (one command)

```bash
curl -fsSL https://raw.githubusercontent.com/Onlyaguest/ViviStableSkills/main/yao-prompt-router/install.sh | bash
```

That's it. No need to clone any repo. Restart Claude Code and start using.

## Usage

In Claude Code, describe your need in natural language:

| You say | Router does |
|---|---|
| "帮我写一篇小红书种草文" | Matches Xiaohongshu Expert |
| "优化一下这个标题" | Matches Title Optimizer |
| "写个抖音短视频脚本" | Matches Douyin Viral Planner |
| "帮我做个PPT" | Recommends `any2deck` if installed |
| "分析竞品的GEO策略" | Matches GEO Competitor Analysis |
| "帮我生成一份合同" | Matches Contract Generator |

## What's Inside

9 categories, 102 templates:

| Category | Count | Examples |
|---|---|---|
| AI Methods | 8 | Meta prompts, reverse engineering |
| AI Work | 10 | Contracts, PPT, landing pages |
| AI Learning | 3 | Memory techniques, habit building |
| AI Life | 2 | Health reports, children's songs |
| AI Education | 1 | Interactive learning pages |
| AI Content | 46 | Copywriting, platform ops, 13 industry experts |
| AI Coding | 1 | System architecture |
| AI Marketing | 28 | GEO full pipeline |
| AI Thinking | 3 | Memory palace, self-critique |

Browse all 102 templates: [docs/prompt-catalog.md](docs/prompt-catalog.md)

## Uninstall

```bash
rm -rf ~/.claude/skills/yao-*/
```

## Docs

- [SKILL.md](./SKILL.md) — Routing logic and execution flow
- [docs/prompt-catalog.md](docs/prompt-catalog.md) — Full catalog with descriptions
