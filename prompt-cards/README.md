# Prompt Cards

Modular prompt card system for AI agents. Load specialized capabilities on demand.

## Quick Start

```bash
# Browse cards
find . -name "*.md" -not -path "./templates/*" -not -name "SKILL.md" -not -name "README.md"

# Use a card
cat meta/frontend-aesthetics.md
```

## Available Cards

| Type | Card | File |
|------|------|------|
| Meta | Frontend Aesthetics Guide | `meta/frontend-aesthetics.md` |
| Role | Pop Art Web Generator | `roles/pop-art-web-generator.md` |
| Workflow | Prompt Co-Pilot | `workflows/prompt-copilot.md` |
| Workflow | AgoraRead | `workflows/agoraread.md` |

## Card Types

- **Meta** — Modifies behavior (stackable, persistent)
- **Role** — Transforms personality (exclusive, one at a time)
- **Workflow** — Structured process (time-bound, 30-90 min)

## Create New Cards

```bash
cp templates/card-template.md meta/my-card.md
# Edit frontmatter and content
```

## Full Documentation

See [SKILL.md](./SKILL.md) for complete reference.
