# Prompt Cards System

Modular prompt card system for AI agents with plug-and-play architecture.

## Quick Start

```bash
# Install
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills/prompt-cards

# Browse cards
find . -name "*.md" -not -path "./templates/*"

# Use a card
cat meta/frontend-aesthetics.md
```

## Available Cards

### Meta Prompts (1)
- 🎨 **Frontend Aesthetics Guide** - Anti-AI-slop design principles

### Role Cards (1)
- 🎨 **Pop Art Web Generator** - Generate pop art style web pages

### Workflow Cards (2)
- 🧭 **Prompt Co-Pilot** - Collaborative prompt creation (30-60 min)
- 📚 **AgoraRead Workflow** - Content analysis and synthesis

## Architecture

```
prompt-cards/
├── meta/          # Meta prompts (stackable)
├── roles/         # Role cards (exclusive)
└── workflows/     # Workflow cards (time-bound)
```

**Three Types:**
- **Meta** - Modify behavior (can stack)
- **Role** - Transform personality (one at a time)
- **Workflow** - Structured process (time-bound)

## Usage Examples

### Enhanced Design
```bash
cat meta/frontend-aesthetics.md
cat roles/pop-art-web-generator.md
# → Pop art style + anti-AI-slop principles
```

### Prompt Creation
```bash
cat workflows/prompt-copilot.md
# → 3-phase collaborative process
```

### Content Analysis
```bash
cat workflows/agoraread.md
# → Structured analysis workflow
```

## Creating New Cards

```bash
# Copy template
cp templates/card-template.md meta/my-card.md

# Edit frontmatter and content
---
name: my-card
type: meta|role|workflow
description: What it does
version: 1.0.0
---
```

## Integration

### OpenClaw
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/Onlyaguest/ViviStableSkills.git vivi-skills
ln -s vivi-skills/prompt-cards .
```

### Claude Code / Cursor
```bash
git clone https://github.com/Onlyaguest/ViviStableSkills.git skills
cat skills/prompt-cards/roles/pop-art-web-generator.md
```

### Custom Agents
```python
with open('meta/frontend-aesthetics.md') as f:
    prompt_card = f.read()
system_prompt = base_prompt + "\n\n" + prompt_card
```

## Card Specifications

| Type | Size | Tokens | Stackable | Duration |
|------|------|--------|-----------|----------|
| Meta | 2-5KB | 500-1500 | Yes | Persistent |
| Role | 5-15KB | 1500-4000 | No | Until switched |
| Workflow | 5-15KB | 1500-4000 | No | 30-90 min |

## Best Practices

1. Start with one card at a time
2. Test combinations carefully
3. Meta prompts: 3-5 max
4. Roles: 1 at a time
5. Document what works

## Documentation

See [SKILL.md](./SKILL.md) for complete documentation.

## License

MIT

## Support

- Issues: https://github.com/Onlyaguest/ViviStableSkills/issues

---

**Made with ❤️ by Vivi**
