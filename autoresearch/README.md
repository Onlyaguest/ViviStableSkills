# autoresearch

Scaffold and track an iterative skill-improvement loop. This is the stable wrapper around the method: lock a checklist, measure a baseline, change one thing at a time, score again, and keep or revert based on evidence.

## Commands

Initialize a workspace:

```bash
python3 main.py init --root /tmp/autoresearch-demo --skill-name "landing-page-skill" --author Developer_Lead --questions "标题是否具体?|是否没有 buzzwords?|CTA 是否具体?"
```

Score one run:

```bash
python3 main.py score --skill-name "landing-page-skill" --answers y,n,y
```

Append an iteration log:

```bash
python3 main.py log-iteration --root /tmp/autoresearch-demo --iteration iter-01 --change "Add explicit headline rule" --before 56 --after 72 --keep --notes "headline quality improved"
```

## Validation

Minimum validation:

```bash
python3 -m py_compile main.py
python3 main.py score --skill-name "landing-page-skill" --answers y,n,y
```

Recommended end-to-end validation:

```bash
python3 main.py init --root /tmp/autoresearch-demo --skill-name "landing-page-skill" --author Developer_Lead --questions "标题是否具体?|是否没有 buzzwords?|CTA 是否具体?"
python3 main.py log-iteration --root /tmp/autoresearch-demo --iteration iter-01 --change "Add explicit headline rule" --before 56 --after 72 --keep
```
