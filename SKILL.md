---
name: yt-notebooklm-bridge
description: >
  Extracts all video URLs from a YouTube channel and saves as a space-separated
  .md file for NotebookLM import. Supports @handle, /channel/, and /c/ URL formats
  with optional video count limit. Use when user mentions "NotebookLM", "做成源",
  "频道提取", "extract channel", "制作源文件", or provides a YouTube channel URL
  with intent to import into NotebookLM.
license: MIT
compatibility: >
  Requires Python 3.8+ and yt-dlp (brew install yt-dlp or pip install yt-dlp).
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
metadata:
  author: acchaacc
  version: "1.0.0"
---

# YouTube → NotebookLM Source Generator

## Script Directory

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/extract_channel_urls.py`

## Workflow

### Step 1: Check Environment

```bash
yt-dlp --version
```

If not installed, run `brew install yt-dlp` or `pip install yt-dlp`.

### Step 2: Get Channel URL

If user hasn't provided a channel URL, ask for one. Supported formats:
- `https://www.youtube.com/@ChannelName`
- `https://www.youtube.com/channel/UCXXXXXXX`
- `https://www.youtube.com/c/ChannelName`

Ask if user wants to limit video count (optional).

### Step 3: Extract Videos

```bash
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>"
```

With video limit:
```bash
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --max-videos 50
```

Custom output path:
```bash
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --output ~/Desktop/custom.md
```

Run `python3 ${SKILL_DIR}/scripts/extract_channel_urls.py --help` for full options.

### Step 4: Report Results

After extraction, report:
- File path (default: `~/Desktop/<channel_name>_notebooklm.md`)
- Number of videos extracted

Then guide user to import into NotebookLM:
1. Open the generated `.md` file
2. Copy video URLs
3. Go to [notebooklm.google.com](https://notebooklm.google.com)
4. Click **"Add source"** → select **"YouTube"**
5. Paste URLs one at a time into the YouTube input

## Troubleshooting

| Issue | Fix |
|-------|-----|
| yt-dlp not found | `brew install yt-dlp` or `pip install yt-dlp` |
| No videos extracted | Verify URL is a channel page, not a single video |
| Timeout | Use `--max-videos` to limit count |
