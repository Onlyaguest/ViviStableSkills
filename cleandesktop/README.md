# CleanDesktop

Auto-archive desktop files into weekly folders with CSV logging.

## Setup

```bash
cd cleandesktop
cp .env.example .env   # Optional: edit paths
chmod +x bin/*.sh
```

## Usage

```bash
# Preview (no files moved)
python3 main.py archive --dry-run

# Archive with GUI category picker (macOS)
./bin/cleandesktop.sh --gui --yes

# Archive with explicit category, skip confirmation
python3 main.py archive --category work --yes

# Query recent archives
python3 main.py list --limit 10

# Show statistics
python3 main.py stats
```

## Configuration

Set in `.env` or as environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CLEANDESKTOP_SOURCE` | `~/Desktop` | Directory to clean |
| `CLEANDESKTOP_ARCHIVE` | `~/Desktop/archive` | Archive destination |
| `CLEANDESKTOP_LOG` | `<archive>/archive_log.csv` | Log file path |
| `CLEANDESKTOP_CATEGORY` | `other` | Default category |

## Output

```
~/Desktop/archive/
  by-week/2025.08.18-2025.08.24/   # Weekly folders
  images-archive/                    # Image copies
  docs-archive/                      # Document copies
  sheets-archive/                    # Spreadsheet copies
  archive_log.csv                    # Operation log
```

## Categories

`work` | `personal` | `project` | `notes` | `other`

## File Types

images, docs, sheets, videos, audio, archives, code, other

See [SKILL.md](./SKILL.md) for full reference.
