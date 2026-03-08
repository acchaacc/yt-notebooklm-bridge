---
name: notebooklm-bridge
description: >
  Prepares multi-platform content as NotebookLM sources. Extracts URLs from
  YouTube channels and Apple Podcasts, saves as space-separated .md files for
  NotebookLM import. Supports keyword filtering for both platforms. Use when user
  mentions "NotebookLM", "做成源", "制作源", "频道提取", "播客提取",
  or provides YouTube channel / Apple Podcasts URLs with intent to import into NotebookLM.
license: MIT
compatibility: >
  YouTube: requires Python 3.8+ and yt-dlp. Podcasts: requires Python 3.8+ only (zero deps).
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
metadata:
  author: acchaacc
  version: "2.0.0"
---

# NotebookLM Source Bridge

Prepares content from YouTube and Apple Podcasts as NotebookLM sources.

## Script Directory

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Detect source type from user's URL and run the appropriate script

## Source Type Detection

| URL Pattern | Script | Output |
|-------------|--------|--------|
| `youtube.com`, `youtu.be` | `extract_channel_urls.py` | `.md` file with space-separated video URLs |
| `podcasts.apple.com` or RSS feed | `extract_podcast_episodes.py` | `.md` file with space-separated audio URLs |

## Workflow: YouTube Channel

```bash
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>"
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --max-videos 50
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --filter "keyword1,keyword2"
```

Output: `~/Desktop/<channel_name>_notebooklm.md` — user copies URLs into NotebookLM YouTube source input.

## Workflow: Apple Podcasts

```bash
# Extract all episode URLs
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>"

# Filter by keywords and extract
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2"

# List matching episodes without saving
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2" --list

# Limit episode count
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2" --max-episodes 10
```

Output: `~/Desktop/<podcast_name>_notebooklm.md` — audio URLs space-separated, same format as YouTube output.

Run `--help` on either script for full CLI options.

## Import Guide

**YouTube** → NotebookLM "Add source" → "YouTube" → paste URLs one at a time

**Podcasts** → NotebookLM "Add source" → "Website" → paste Apple Podcasts episode URLs one at a time

## Troubleshooting

| Issue | Fix |
|-------|-----|
| yt-dlp not found | `brew install yt-dlp` or `pip install yt-dlp` |
| No videos/episodes found | Check URL format |
| Podcast RSS fetch failed | Try direct RSS feed URL instead of Apple Podcasts URL |
| iTunes API returns max 200 episodes | Older episodes beyond 200 won't be included |
