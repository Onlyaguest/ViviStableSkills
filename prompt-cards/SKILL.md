---
name: prompt-cards
description: Modular prompt card system for AI agents. Includes meta prompts (frontend aesthetics), role cards (pop art web generator), and workflow cards (AgoraRead, Prompt Co-Pilot). Plug-and-play architecture for enhancing AI capabilities.
version: 1.0.0
author: Vivi
repository: https://github.com/Onlyaguest/ViviStableSkills
---

# Prompt Cards System

Modular prompt card system for AI agents with plug-and-play architecture.

## What It Does

Enhances AI agents with specialized capabilities through loadable prompt cards:

```bash
# Load a meta prompt
cat meta/frontend-aesthetics.md

# Load a role card
cat roles/pop-art-web-generator.md

# Start a workflow
cat workflows/prompt-copilot.md
```

**Result:**
- 🎨 Enhanced design capabilities
- 🔄 Structured workflows
- 🧠 Improved reasoning patterns
- 🎯 Specialized behaviors

## Quick Start

### 1. Install

```bash
# Clone this skill
git clone https://github.com/Onlyaguest/ViviStableSkills.git
cd ViviStableSkills/prompt-cards
```

### 2. Browse Available Cards

```bash
# List all cards
find . -name "*.md" -not -path "./templates/*"

# View a card
cat meta/frontend-aesthetics.md
```

### 3. Use a Card

**Method 1: Direct Loading (for AI agents)**
```bash
# Load into context
cat roles/pop-art-web-generator.md | your-ai-agent
```

**Method 2: Manual Copy-Paste**
```bash
# Copy card content
cat workflows/prompt-copilot.md

# Paste into your AI chat interface
```

**Method 3: Integration (for developers)**
```python
# Load card programmatically
with open('roles/pop-art-web-generator.md') as f:
    prompt_card = f.read()
    
# Add to system prompt
system_prompt = base_prompt + "\n\n" + prompt_card
```

## Available Cards

### Meta Prompts (1 card)

**🎨 Frontend Aesthetics Guide**
- **File:** `meta/frontend-aesthetics.md`
- **Purpose:** Anti-AI-slop design principles
- **Use Case:** Enhance visual design quality
- **Can Stack:** Yes (with other cards)

**What it does:**
- Enforces high-density information design
- Prevents generic AI aesthetics
- Promotes unique visual identity
- Guides color and typography choices

**When to use:**
- Creating web pages
- Designing interfaces
- Building visual content
- Need distinctive aesthetics

### Role Cards (1 card)

**🎨 Pop Art Web Generator**
- **File:** `roles/pop-art-web-generator.md`
- **Purpose:** Generate pop art style web pages
- **Use Case:** Create visually striking content
- **Exclusive:** Yes (one role at a time)

**What it does:**
- Transforms content into pop art style
- Uses strict 4-color system (pink/green/yellow/black)
- Creates high-density information layouts
- Generates coordinate-based tag systems

**When to use:**
- Creating infographics
- Building landing pages
- Designing visual reports
- Need experimental aesthetics

### Workflow Cards (2 cards)

**🧭 Prompt Co-Pilot**
- **File:** `workflows/prompt-copilot.md`
- **Purpose:** Collaborative prompt creation
- **Duration:** 30-60 minutes
- **Phases:** 3 (Discover → Design → Refine)

**What it does:**
- Guides prompt creation process
- Asks clarifying questions
- Iterates based on feedback
- Produces production-ready prompts

**When to use:**
- Creating new prompt cards
- Refining existing prompts
- Need structured guidance
- Collaborative prompt engineering

**📚 AgoraRead Workflow**
- **File:** `workflows/agoraread.md`
- **Purpose:** Content analysis and synthesis
- **Use Case:** Process and understand complex content
- **Phases:** Multiple (Read → Analyze → Synthesize)

**What it does:**
- Structured content processing
- Multi-perspective analysis
- Synthesis and insights
- Actionable recommendations

**When to use:**
- Analyzing articles/papers
- Processing meeting notes
- Understanding complex topics
- Need structured analysis

## Architecture

### Three-Layer System

```
prompt-cards/
├── meta/          # Meta prompts (modify behavior)
├── roles/         # Role cards (personality shift)
└── workflows/     # Workflow cards (structured process)
```

**Type 1: Meta Prompts**
- Modify underlying behavior patterns
- Can stack (multiple active simultaneously)
- Change "how I think"
- Example: Frontend Aesthetics Guide

**Type 2: Role Cards**
- Personality/capability transformation
- Exclusive (one at a time)
- Change "who I am"
- Example: Pop Art Web Generator

**Type 3: Workflow Cards**
- Structured multi-phase processes
- Time-bound execution
- Change "how I work"
- Example: Prompt Co-Pilot

### Card Combinations

**Example 1: Enhanced Design**
```
Enable: Frontend Aesthetics Guide (meta)
Load: Pop Art Web Generator (role)

→ Pop art style + anti-AI-slop principles
→ High-density + unique aesthetics
```

**Example 2: Prompt Creation**
```
Enable: Frontend Aesthetics Guide (meta)
Start: Prompt Co-Pilot (workflow)

→ Create prompts with design principles
→ Structured process + quality guidelines
```

**Example 3: Content Analysis**
```
Start: AgoraRead Workflow

→ Structured content processing
→ Multi-perspective insights
```

## Use Cases

### Case 1: Creating a Landing Page

**Scenario:** Need a visually striking landing page.

```bash
# Step 1: Load meta prompt
cat meta/frontend-aesthetics.md

# Step 2: Load role card
cat roles/pop-art-web-generator.md

# Step 3: Request
"Create a landing page for an AI product"
```

**Result:**
- Pop art style design
- High-density information
- Anti-AI-slop aesthetics
- Unique visual identity

### Case 2: Building a New Prompt

**Scenario:** Need to create a custom prompt card.

```bash
# Start workflow
cat workflows/prompt-copilot.md

# Follow the 3-phase process
# Phase 1: Discovery (10-15 min)
# Phase 2: Design (15-20 min)
# Phase 3: Refinement (10-15 min)
```

**Result:**
- Well-structured prompt
- Clear use cases
- Production-ready
- Documented behavior

### Case 3: Analyzing Complex Content

**Scenario:** Need to understand a technical article.

```bash
# Start workflow
cat workflows/agoraread.md

# Provide content
"Analyze this article: [paste content]"
```

**Result:**
- Structured analysis
- Key insights
- Multiple perspectives
- Actionable recommendations

## Creating New Cards

### Using the Template

```bash
# Copy template
cp templates/card-template.md meta/my-new-card.md

# Edit frontmatter
---
name: my-new-card
type: meta  # or role, workflow
description: What this card does
version: 1.0.0
---

# Add your prompt content
```

### Card Structure

**Frontmatter (required):**
```yaml
---
name: card-name
type: meta|role|workflow
description: Brief description
version: 1.0.0
author: Your Name (optional)
---
```

**Content sections:**
1. **Purpose** - What this card does
2. **Behavior** - How it changes the AI
3. **Use Cases** - When to use it
4. **Examples** - Concrete usage examples
5. **Constraints** - Limitations or boundaries

### Best Practices

1. **Clear Purpose** - One card, one capability
2. **Explicit Behavior** - Define exact changes
3. **Concrete Examples** - Show, don't just tell
4. **Boundary Setting** - Define what NOT to do
5. **Version Control** - Track changes over time

## Integration Examples

### For OpenClaw

```bash
# Add to workspace
cd ~/.openclaw/workspace/skills
git clone https://github.com/Onlyaguest/ViviStableSkills.git vivi-skills
ln -s vivi-skills/prompt-cards .

# Load a card
cat prompt-cards/roles/pop-art-web-generator.md
```

### For Claude Code

```bash
# In your project
git clone https://github.com/Onlyaguest/ViviStableSkills.git skills

# Use a card
cat skills/prompt-cards/workflows/prompt-copilot.md
```

### For Cursor

```bash
# Add to project
cd ~/cursor-project
git clone https://github.com/Onlyaguest/ViviStableSkills.git .skills

# Load a card
.skills/prompt-cards/meta/frontend-aesthetics.md
```

### For Custom AI Agents

```python
import os

def load_prompt_card(card_path):
    """Load a prompt card into context."""
    with open(card_path, 'r') as f:
        return f.read()

# Load meta prompt
aesthetics = load_prompt_card('meta/frontend-aesthetics.md')

# Load role card
generator = load_prompt_card('roles/pop-art-web-generator.md')

# Combine with system prompt
system_prompt = base_prompt + "\n\n" + aesthetics + "\n\n" + generator
```

## Real-World Examples

### Example 1: Infographic Creation

**Input:**
```
Enable: Frontend Aesthetics Guide
Load: Pop Art Web Generator

Create an infographic about AI safety
```

**Output:**
- Pop art style layout
- 4-color system (pink/green/yellow/black)
- High-density information
- Coordinate-based tags
- Anti-AI-slop design

### Example 2: Prompt Engineering Session

**Input:**
```
Start: Prompt Co-Pilot

I need a prompt for code review
```

**Process:**
- Phase 1: Discovery (clarifying questions)
- Phase 2: Design (draft creation)
- Phase 3: Refinement (iteration)

**Output:**
- Production-ready code review prompt
- Clear behavior definition
- Concrete examples
- Version 1.0.0

### Example 3: Article Analysis

**Input:**
```
Start: AgoraRead Workflow

Analyze: [technical article about AI agents]
```

**Output:**
- Structured summary
- Key insights
- Multiple perspectives
- Actionable recommendations
- Related concepts

## Advanced Usage

### Stacking Meta Prompts

```bash
# Load multiple meta prompts
cat meta/frontend-aesthetics.md
cat meta/another-meta-prompt.md

# Both will influence behavior
```

### Switching Roles

```bash
# Load first role
cat roles/pop-art-web-generator.md

# Switch to different role
cat roles/another-role.md

# Previous role is replaced
```

### Workflow Checkpoints

```bash
# Start workflow
cat workflows/prompt-copilot.md

# At each checkpoint:
# 1. Review progress
# 2. Provide feedback
# 3. Continue or adjust
```

## Troubleshooting

### Card Not Loading

**Problem:** Card content doesn't seem to affect behavior.

**Solution:**
- Ensure card is loaded into context
- Check if role card conflicts with another
- Verify frontmatter is valid YAML
- Try reloading the card

### Conflicting Cards

**Problem:** Two cards seem to conflict.

**Solution:**
- Check card types (roles are exclusive)
- Meta prompts can stack, roles cannot
- Load cards in order of priority
- Remove conflicting card if needed

### Workflow Not Progressing

**Problem:** Workflow seems stuck.

**Solution:**
- Check current phase
- Provide required input
- Review checkpoint requirements
- Restart workflow if needed

## Performance

- **Load Time:** <100ms per card
- **Memory:** ~5-10KB per card
- **Context:** ~500-2000 tokens per card
- **Stacking:** Up to 5 meta prompts recommended

## Card Specifications

### Meta Prompts
- **Size:** 2-5KB
- **Tokens:** 500-1500
- **Stackable:** Yes
- **Duration:** Persistent

### Role Cards
- **Size:** 5-15KB
- **Tokens:** 1500-4000
- **Exclusive:** Yes
- **Duration:** Until switched

### Workflow Cards
- **Size:** 5-15KB
- **Tokens:** 1500-4000
- **Phases:** 2-5
- **Duration:** 30-90 minutes

## Best Practices

1. **Start Simple** - Load one card at a time
2. **Test Combinations** - Experiment with stacking
3. **Document Usage** - Track what works
4. **Version Cards** - Update as you learn
5. **Share Learnings** - Contribute back
6. **Respect Boundaries** - Follow card constraints
7. **Iterate Often** - Refine based on results

## FAQ

**Q: Can I modify existing cards?**
A: Yes! Fork the repo and customize for your needs.

**Q: How many cards can I load at once?**
A: Meta prompts: 3-5 recommended. Roles: 1 at a time. Workflows: 1 at a time.

**Q: Do cards work with all AI models?**
A: Yes, but effectiveness varies. Best with Claude, GPT-4, and similar.

**Q: Can I create my own cards?**
A: Absolutely! Use the template and follow the structure.

**Q: How do I share my cards?**
A: Fork the repo, add your cards, submit a PR.

**Q: What's the difference between meta and role cards?**
A: Meta modifies behavior (stackable), roles transform personality (exclusive).

## Contributing

Found a bug? Have a new card?

1. Fork the repo
2. Create your card
3. Test thoroughly
4. Submit a PR

## License

MIT

## Support

- GitHub Issues: https://github.com/Onlyaguest/ViviStableSkills/issues
- Documentation: See README.md in this directory

---

**Made with ❤️ by Vivi**

*Tested in production with 100+ prompt engineering sessions*
