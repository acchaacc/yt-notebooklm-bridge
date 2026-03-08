#!/usr/bin/env python3
"""
Extract all video URLs from a YouTube channel and save as markdown file.
Output format: URLs separated by spaces, saved as .md file for NotebookLM import.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def extract_channel_info(channel_url):
    """Extract channel name using yt-dlp or URL parsing."""
    # Try yt-dlp first with playlist_title
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--playlist-end", "1",
                "--print", "%(playlist_title)s",
                channel_url,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            name = result.stdout.strip().split("\n")[0]
            if name and name != "NA" and name != "nan":
                # Remove common suffixes like " - Videos"
                for suffix in [" - Videos", " - 视频", " - uploads"]:
                    if name.endswith(suffix):
                        name = name[: -len(suffix)]
                return name
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Fallback: extract from URL
    import re

    # Match @handle format
    match = re.search(r"@([^/?\s]+)", channel_url)
    if match:
        return match.group(1)

    # Match /channel/NAME or /c/NAME
    match = re.search(r"/(?:channel|c)/([^/?\s]+)", channel_url)
    if match:
        return match.group(1)

    return None


def extract_video_urls(channel_url, max_videos=None, filter_keywords=None):
    """Extract all video URLs from a YouTube channel."""
    if filter_keywords:
        # Need titles for filtering
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(url)s\t%(title)s",
            channel_url,
        ]
    else:
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(url)s",
            channel_url,
        ]

    if max_videos and not filter_keywords:
        cmd.extend(["--playlist-end", str(max_videos)])

    print(f"Extracting video URLs from: {channel_url}")
    print("This may take a moment for channels with many videos...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            print(f"Error: {result.stderr.strip()}")
            return []

        urls = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            if filter_keywords:
                parts = line.split("\t", 1)
                url_part = parts[0]
                title_part = parts[1] if len(parts) > 1 else ""
                # Check if any keyword matches the title
                if not any(kw.lower() in title_part.lower() for kw in filter_keywords):
                    continue
            else:
                url_part = line

            # Ensure full YouTube URL format
            if url_part.startswith("http"):
                urls.append(url_part)
            else:
                urls.append(f"https://www.youtube.com/watch?v={url_part}")

        # Apply max_videos after filtering
        if filter_keywords and max_videos:
            urls = urls[:max_videos]

        return urls

    except subprocess.TimeoutExpired:
        print("Error: Extraction timed out. Try using --max-videos to limit.")
        return []


def save_as_markdown(urls, channel_name, output_path):
    """Save URLs as markdown file with space separation."""
    # URLs separated by spaces
    url_string = " ".join(urls)

    content = url_string

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract YouTube channel video URLs for NotebookLM import"
    )
    parser.add_argument(
        "channel_url",
        help="YouTube channel URL (e.g., https://www.youtube.com/@ChannelName)",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum number of videos to extract (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: ~/Desktop/<channel_name>_notebooklm.md)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Comma-separated keywords to filter videos by title",
    )

    args = parser.parse_args()

    # Check yt-dlp
    if not check_yt_dlp():
        print("Error: yt-dlp is not installed.")
        print("Install with: brew install yt-dlp  or  pip install yt-dlp")
        sys.exit(1)

    # Get channel name
    channel_name = extract_channel_info(args.channel_url)
    if not channel_name:
        channel_name = "youtube_channel"
    # Clean channel name for filename
    safe_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in channel_name
    )

    # Parse filter keywords
    filter_keywords = None
    if args.filter:
        filter_keywords = [k.strip() for k in args.filter.split(",") if k.strip()]

    # Extract URLs
    urls = extract_video_urls(args.channel_url, args.max_videos, filter_keywords)

    if not urls:
        print("No videos found. Please check the channel URL.")
        sys.exit(1)

    print(f"\nFound {len(urls)} videos.")

    # Determine output path
    if args.output:
        output_path = os.path.expanduser(args.output)
    else:
        desktop = os.path.expanduser("~/Desktop")
        output_path = os.path.join(desktop, f"{safe_name}_notebooklm.md")

    # Save
    save_as_markdown(urls, channel_name, output_path)

    print(f"\nSaved to: {output_path}")
    print(f"Total URLs: {len(urls)}")
    print(f"\nYou can now import this file as a source in NotebookLM.")


if __name__ == "__main__":
    main()
