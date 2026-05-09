---
name: autoresearch
description: Run a measured improvement loop for a skill by defining a yes/no checklist, capturing a baseline, scoring candidate outputs, and logging each iteration's keep/revert decision. Use when a skill works inconsistently and you want evidence-driven iteration instead of random prompt edits.
version: 1.0.0
author: Vivi
tags: [research, iteration, evaluation, prompt, skill-quality]
platforms: [all]
dependencies:
  - python3
---

# autoresearch

Turn the method into a stable workflow. This skill does not pretend to be a fully autonomous optimizer yet; instead it gives the team a reproducible workspace for iterative skill improvement with checklist scoring, baseline capture, and iteration logs.

## Use this skill when

- A skill works 70% of the time and fails the other 30%
- You want measured iteration instead of ad hoc prompt editing
- The team needs a checklist-driven loop with changelog and baseline evidence
- A future agent should be able to resume from previous iteration history

## Workflow

1. Initialize an `autoresearch/` workspace.
2. Define 3-6 yes/no checklist questions.
3. Lock a test input and record the baseline.
4. Make one change only.
5. Score the new output.
6. Keep or revert the change and append the result to the changelog.

## Commands

Initialize a workspace:

```bash
python3 main.py init --root /tmp/autoresearch-demo --skill-name "landing-page-skill" --author Developer_Lead --questions "标题是否具体?|是否没有 buzzwords?|CTA 是否具体?"
```

Score one run:

```bash
python3 main.py score --skill-name "landing-page-skill" --answers y,n,y
```

Log one iteration:

```bash
python3 main.py log-iteration --root /tmp/autoresearch-demo --iteration iter-01 --change "Add explicit headline rule" --before 56 --after 72 --keep
```

## Inputs and outputs

- Input: target skill name, checklist questions, yes/no answers, iteration changes, baseline notes
- Output: `autoresearch/` workspace with `checklist.md`, `baseline.md`, `CHANGELOG.md`, `runbook.md`, and optional JSONL scoring logs

## Validation

Minimum validation commands:

```bash
python3 -m py_compile main.py
```

```bash
python3 main.py score --skill-name "landing-page-skill" --answers y,n,y
```

## Constraints

- This is a research loop scaffold, not a fully autonomous optimizer
- Checklist quality determines result quality; vague questions will poison the loop
- Only change one thing at a time, or the changelog stops being useful
