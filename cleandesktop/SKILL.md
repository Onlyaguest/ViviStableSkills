---
name: cleandesktop
description: Desktop file organizer - auto-archive by week with type classification and CSV logging.
version: 2.1.0
author: Vivi
tags: [productivity, desktop, archive, cleanup]
platforms: [macos, linux]
dependencies:
  - python3
---

# CleanDesktop

Auto-archive desktop files into weekly folders with dual-tag classification (category + type) and CSV logging.

## Features

- Weekly folder organization with date-prefixed filenames
- Dual-tag system: category (work/personal/project/notes/other) + file type (images/docs/sheets/etc.)
- Extra copies for images, docs, and sheets in type-specific folders
- CSV log for all operations (queryable via `list` and `stats` commands)
- GUI category picker on macOS (AppleScript), terminal fallback elsewhere
- `--dry-run` preview mode

## Quick Start

```bash
cd cleandesktop
cp .env.example .env   # Edit paths if needed

# Preview what would happen
python3 main.py archive --dry-run

# Archive with GUI category picker (macOS)
./bin/cleandesktop.sh --gui --yes

# Archive with explicit category
python3 main.py archive --category work --yes
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `archive` | Move desktop files to archive | `archive --category work --yes` |
| `archive --dry-run` | Preview without moving | `archive --dry-run` |
| `archive --gui` | GUI category picker (macOS) | `archive --gui --yes` |
| `list` | Query archive log | `list --category work --limit 10` |
| `list --type <t>` | Filter by file type | `list --type images` |
| `list --week <w>` | Filter by week folder | `list --week 2025.08.21-2025.08.27` |
| `stats` | Show archive statistics | `stats` |

## Configuration

All via environment variables (or `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `CLEANDESKTOP_SOURCE` | Source directory to clean | `~/Desktop` |
| `CLEANDESKTOP_ARCHIVE` | Archive root directory | `~/Desktop/archive` |
| `CLEANDESKTOP_LOG` | CSV log file path | `<archive>/archive_log.csv` |
| `CLEANDESKTOP_CATEGORY` | Default category tag | `other` |

Legacy variables (`DESKTOP_PATH`, `ARCHIVE_PATH`, `LOG_PATH`, `DEFAULT_CATEGORY`) are also supported as fallback.

## Output Structure

```
~/Desktop/archive/
  by-week/
    2025.08.18-2025.08.24/
      2025.08.20 meeting-notes.pdf
      2025.08.21 screenshot.png
  images-archive/       # Image copies
  docs-archive/         # Document copies
  sheets-archive/       # Spreadsheet copies
  archive_log.csv       # Operation log
```

## Log Fields

| Field | Description |
|-------|-------------|
| `archived_at` | Timestamp (ISO format) |
| `original_name` | Original filename |
| `new_name` | Archived filename (with date prefix) |
| `category_tag` | Category tag |
| `type_tag` | File type tag |
| `week_folder` | Week folder name |
| `src_path` | Original path |
| `dest_path` | Archived path |

## Supported File Types

| Type | Extensions |
|------|-----------|
| images | png, jpg, jpeg, gif, bmp, tiff, webp, heic, svg |
| docs | txt, md, pdf, doc, docx, rtf, pages |
| sheets | xlsx, xls, csv, numbers |
| videos | mp4, mov, avi, mkv, wmv |
| audio | mp3, wav, aac, flac, m4a |
| archives | zip, rar, 7z, tar, gz |
| code | py, js, ts, html, css, java, swift, go, rs, sh |

## Troubleshooting

**Log not updating?**
Check that the archive directory exists and is writable. Run manually and look for error output.

**Can't find archived file?**
Query the log: `python3 main.py list --limit 10` and check the `dest_path` field in the CSV.

**GUI dialog not appearing?**
`--gui` requires macOS. On other platforms it falls back to terminal selection.
