---
name: notebooklm-bridge
description: >
  Prepares multi-platform content as NotebookLM sources. Extracts YouTube channel
  video URLs (space-separated .md file) and downloads Apple Podcasts episodes as
  audio files. Supports keyword filtering for both platforms. Use when user mentions
  "NotebookLM", "做成源", "制作源", "频道提取", "播客下载", "podcast download",
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
| `youtube.com`, `youtu.be` | `extract_channel_urls.py` | `.md` file with space-separated URLs |
| `podcasts.apple.com` or RSS feed | `extract_podcast_episodes.py` | Downloaded audio files |

## Workflow: YouTube Channel

```bash
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>"
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --max-videos 50
python3 ${SKILL_DIR}/scripts/extract_channel_urls.py "<channel_url>" --filter "keyword1,keyword2"
```

Output: `~/Desktop/<channel_name>_notebooklm.md` — user copies URLs into NotebookLM YouTube source input.

## Workflow: Apple Podcasts

```bash
# List all episodes
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --list

# Filter and list by keywords
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2" --list

# Download filtered episodes
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2"

# Limit download count
python3 ${SKILL_DIR}/scripts/extract_podcast_episodes.py "<podcast_url>" --filter "keyword1,keyword2" --max-episodes 10
```

Output: `~/Desktop/<podcast_name>/` folder with audio files — user uploads to NotebookLM as audio sources.

Run `--help` on either script for full CLI options.

## Import Guide

**YouTube** → NotebookLM "Add source" → "YouTube" → paste URLs one at a time

**Podcasts** → NotebookLM "Add source" → upload audio files (max 200MB/file, 50 sources/notebook)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| yt-dlp not found | `brew install yt-dlp` or `pip install yt-dlp` |
| No videos/episodes found | Check URL format |
| Podcast RSS fetch failed | Try direct RSS feed URL instead of Apple Podcasts URL |
| Audio file too large | NotebookLM limit is 200MB per file |
