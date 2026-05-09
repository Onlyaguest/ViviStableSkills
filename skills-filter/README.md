# skills-filter

Decision filter for new skills. It turns the original 5-question rubric into a small CLI so humans and agents can score a candidate skill consistently before spending time building it.

## Why this exists

- Avoid building generic AI wrappers with no moat
- Force a quick yes/no conversation before implementation
- Keep Codex and CC using the same screening rubric

## Commands

Print the five questions:

```bash
python3 main.py --template
```

Run a built-in example:

```bash
python3 main.py --example lawyer-email-assistant
```

Score a real candidate:

```bash
python3 main.py --title "创业者精力风控系统" --answers y,y,y,y,y
```

Interactive mode:

```bash
python3 main.py --interactive --title "我想做的新 skill"
```

## Validation

Minimum validation:

```bash
python3 main.py --example lawyer-email-assistant
python3 -m py_compile main.py
```

## Output

- Per-question pass/fail
- Total score out of 5
- Decision bucket:
  - `5/5` -> `立即做`
  - `3-4/5` -> `可以做，但需要深化`
  - `1-2/5` -> `不要做`
  - `0/5` -> `绝对不要做`
