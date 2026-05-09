---
name: data-showcase-site
description: Build a static HTML report site from CSV, JSON, Markdown, or HTML inputs. Use when the user wants to turn existing data into a human-readable site, generate a data showcase page, create a static report website, or optionally publish the built site.
version: 1.0.0
author: Vivi
tags: [data, reports, static-site, csv, json, html]
platforms: [all]
dependencies:
  - python3
  - git
---

# data-showcase-site

Turn existing report files into a static site for humans. This skill is for packaging data into readable pages, not for doing heavy analysis from scratch.

## Use this skill when

- The user says "把这个 CSV 做成报告网站"
- The input is already CSV / TSV / JSON / Markdown / HTML
- The user wants a static report site or showcase page
- The user may want to publish the built site after local verification

## Workflow

1. Put report files into `reports/` or point `--reports` to an existing folder.
2. Run the example build first to verify the tool works locally.
3. Run a real build with actual data.
4. Optionally publish only after local output looks correct.

## Commands

Minimum validation:

```bash
python3 main.py build --use-examples
```

Build with real data:

```bash
python3 main.py build --reports /absolute/path/to/reports --out out/site
```

Optional publish:

```bash
python3 main.py publish
```

## Inputs and outputs

- Input: CSV / TSV / JSON / Markdown / HTML report files
- Output: static site files, usually under `out/site/`

## Validation

Minimum validation command:

```bash
python3 main.py build --use-examples
```

Successful build writes a local site with `index.html`.

## Constraints

- This skill assumes the data already exists
- `reports/` and `assets/` should stay out of source control unless intentionally committed
- Publish should happen only after local review of generated pages
