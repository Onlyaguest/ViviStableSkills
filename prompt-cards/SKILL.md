---
name: prompt-cards
description: Modular prompt card system for AI agents with meta prompts, role cards, and workflow cards.
version: 1.0.0
author: Vivi
tags: [prompts, ai-agents, workflow, design]
platforms: [all]
dependencies: []
---

# Prompt Cards Skill

Enhance AI agents with specialized capabilities through loadable prompt cards.

## Features

- Three card types: meta (stackable), role (exclusive), workflow (time-bound)
- Plug-and-play architecture
- Card template for creating new cards
- Works with any AI model (Claude, GPT-4, etc.)

## Quick Start

```bash
# Browse available cards
find . -name "*.md" -not -path "./templates/*" -not -name "SKILL.md" -not -name "README.md"

# Load a card into your AI agent
cat meta/frontend-aesthetics.md

# Combine cards
cat meta/frontend-aesthetics.md roles/pop-art-web-generator.md
```

## Available Cards

### Meta Prompts

| Card | File | Purpose |
|------|------|---------|
| Frontend Aesthetics Guide | `meta/frontend-aesthetics.md` | Anti-AI-slop design principles, high-density layouts |

### Role Cards

| Card | File | Purpose |
|------|------|---------|
| Pop Art Web Generator | `roles/pop-art-web-generator.md` | Generate pop art style web pages with 4-color system |

### Workflow Cards

| Card | File | Purpose |
|------|------|---------|
| Prompt Co-Pilot | `workflows/prompt-copilot.md` | 3-phase collaborative prompt creation (30-60 min) |
| AgoraRead | `workflows/agoraread.md` | Structured content analysis and synthesis |

## Card Types

| Type | Behavior | Stackable | Duration |
|------|----------|-----------|----------|
| **Meta** | Modifies how the AI thinks | Yes (up to 5) | Persistent |
| **Role** | Transforms personality/capability | No (one at a time) | Until switched |
| **Workflow** | Structured multi-phase process | No (one at a time) | 30-90 min |

## Usage Methods

**Direct loading (AI agents):**
```bash
cat roles/pop-art-web-generator.md | your-ai-agent
```

**Programmatic (developers):**
```python
with open('meta/frontend-aesthetics.md') as f:
    card = f.read()
system_prompt = base_prompt + "\n\n" + card
```

**Copy-paste (manual):**
```bash
cat workflows/prompt-copilot.md
# Paste into your AI chat
```

## Card Combinations

```
Meta + Role:    frontend-aesthetics + pop-art-web-generator = styled pop art with anti-slop principles
Meta + Workflow: frontend-aesthetics + prompt-copilot = design-aware prompt engineering
```

## Creating New Cards

```bash
cp templates/card-template.md meta/my-card.md
```

Card frontmatter:
```yaml
---
name: card-name
type: meta|role|workflow
description: What this card does
version: 1.0.0
---
```

Guidelines:
- One card = one capability
- Define explicit behavior changes
- Include concrete examples
- Set clear boundaries

## File Structure

```
prompt-cards/
├── meta/                          # Stackable behavior modifiers
│   └── frontend-aesthetics.md
├── roles/                         # Exclusive personality cards
│   └── pop-art-web-generator.md
├── workflows/                     # Time-bound processes
│   ├── agoraread.md
│   └── prompt-copilot.md
├── templates/
│   └── card-template.md           # Template for new cards
├── SKILL.md
└── README.md
```

## Troubleshooting

**Card not affecting behavior?**
Ensure it's loaded into context. Role cards are exclusive — loading a new one replaces the previous.

**Conflicting cards?**
Meta prompts stack; roles don't. Remove the conflicting role card.
