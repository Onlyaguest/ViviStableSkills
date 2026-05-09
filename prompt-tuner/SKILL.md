---
name: prompt-tuner
description: Test, tune, and regression-check LLM system prompts with a golden dataset. Use when the user wants to optimize a prompt, run prompt regression tests, manage `cases.yaml`, compare expected vs actual outputs, or follow a TDD workflow for prompts.
version: 1.0.0
author: Vivi
tags: [prompt, llm, regression, tuning, tdd]
platforms: [all]
dependencies:
  - python3
  - requests
  - python-dotenv
  - pyyaml
---

# prompt-tuner

Treat prompts like code: `prompt.txt` is the source, `cases.yaml` is the golden dataset, `tuner.py` is the test runner, and `CHANGELOG.md` tracks prompt logic changes.

## Use this skill when

- The user says "帮我优化这个 prompt"
- The user wants prompt regression testing
- The project already uses `cases.yaml`, `prompt.txt`, or a golden dataset
- A prompt behaves badly and needs repeatable debugging
- The team wants TDD for prompts instead of one-off prompt edits

## Workflow

1. Run local structure check first.
2. If files are valid, run real regression tests with configured provider and API key.
3. Add failing cases before editing prompt rules.
4. Update version markers in `prompt.txt` and `CHANGELOG.md` after changes.

## Commands

Local check without API calls:

```bash
python3 tuner.py --check
```

Run full regression:

```bash
python3 tuner.py
```

Optional provider override:

```bash
python3 tuner.py --provider openai --model gpt-4o
```

## Inputs and outputs

- Input: `prompt.txt`, `cases.yaml`, `.env`
- Output: pass/fail table in terminal, plus raw mismatches for failed cases

## Validation

Minimum validation command:

```bash
python3 tuner.py --check
```

This checks:

- required files exist
- `prompt.txt` has a version header
- `cases.yaml` loads correctly
- each case has `input` and `expected`

## Constraints

- Do not change prompt behavior without adding or updating a regression case
- Prefer `--check` for audits and review when API credentials are not configured
- Keep prompt version in `prompt.txt` aligned with `CHANGELOG.md`
