---
name: skills-filter
description: Evaluate whether a proposed skill is worth building by scoring it against five moat-oriented questions: differentiation, vertical fit, learning loop, user difficulty, and defensibility. Use when someone proposes a new skill and you want a fast build / deepen / reject decision before implementation.
version: 1.0.0
author: Vivi
tags: [skills, evaluation, strategy, triage]
platforms: [all]
dependencies:
  - python3
---

# skills-filter

Fast gate for new skill ideas. It prevents the team from spending time on generic wrappers and pushes skill design toward domain knowledge, data loops, workflow integration, and defensibility.

## Use this skill when

- Someone says "我想做一个 XXX skill"
- You need to decide whether a skill idea deserves engineering time
- A proposed skill feels too generic and needs a harder filter
- The team wants a shared rubric before adding new items to `MyStableSkills`

## Workflow

1. Ask the five questions.
2. Score the candidate out of 5.
3. If the score is `5/5`, build it now.
4. If the score is `3-4/5`, deepen the moat first.
5. If the score is `0-2/5`, reject it or redesign it.

## Commands

Show the checklist:

```bash
python3 main.py --template
```

Run a built-in example:

```bash
python3 main.py --example lawyer-email-assistant
```

Score a real proposal:

```bash
python3 main.py --title "创业者精力风控系统" --answers y,y,y,y,y
```

## Questions

1. 跟"直接丢给 AI"有什么明显区别？
2. 有行业偏向性或场景偏向性吗？
3. 会越用越聪明吗？
4. 用户自己很难做到吗？
5. 有壁垒吗？

## Inputs and outputs

- Input: candidate skill idea plus five yes/no judgments
- Output: per-question pass/fail, score out of 5, and a build/deepen/reject decision

## Validation

Minimum validation commands:

```bash
python3 main.py --example lawyer-email-assistant
```

```bash
python3 -m py_compile main.py
```

## Constraints

- This is a triage filter, not a replacement for later product design
- A high score means "worth building", not "already well specified"
- Use it before implementation, not after the team has already sunk the cost
