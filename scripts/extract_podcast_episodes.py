#!/usr/bin/env python3
"""
Extract podcast episodes from Apple Podcasts and download audio files.
Supports keyword filtering, episode limiting, and direct RSS feed URLs.
Zero external dependencies — uses only Python stdlib.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup?id={}&entity=podcast"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_url(url, timeout=30):
    """Fetch URL content with proper headers."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    return urlopen(req, timeout=timeout).read()


def extract_podcast_id(url):
    """Extract Apple Podcasts numeric ID from URL."""
    match = re.search(r"/id(\d+)", url)
    return match.group(1) if match else None


def get_rss_feed_url(podcast_id):
    """Get RSS feed URL from iTunes Lookup API."""
    url = ITUNES_LOOKUP_URL.format(podcast_id)
    data = json.loads(fetch_url(url))
    results = data.get("results", [])
    if not results:
        return None, None
    result = results[0]
    return result.get("feedUrl"), result.get("collectionName", "podcast")


def is_rss_url(url):
    """Check if URL looks like an RSS feed (not Apple Podcasts)."""
    parsed = urlparse(url)
    return "podcasts.apple.com" not in parsed.netloc


def parse_rss_feed(feed_xml):
    """Parse RSS feed XML and extract episode data."""
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")
    if channel is None:
        return None, []

    # Podcast metadata
    podcast_name = ""
    title_el = channel.find("title")
    if title_el is not None and title_el.text:
        podcast_name = title_el.text.strip()

    # Parse episodes
    episodes = []
    itunes_ns = "http://www.itunes.com/dtds/podcast-1.0.dtd"

    for item in channel.findall("item"):
        episode = {}

        # Title
        title_el = item.find("title")
        episode["title"] = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"

        # Description (check multiple fields)
        desc = ""
        for tag in ["description", f"{{{itunes_ns}}}summary"]:
            el = item.find(tag)
            if el is not None and el.text:
                desc = el.text.strip()
                break
        episode["description"] = desc

        # Publication date
        pub_el = item.find("pubDate")
        episode["pub_date"] = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

        # Duration
        dur_el = item.find(f"{{{itunes_ns}}}duration")
        episode["duration"] = dur_el.text.strip() if dur_el is not None and dur_el.text else ""

        # Audio URL from enclosure
        enc_el = item.find("enclosure")
        if enc_el is not None:
            episode["audio_url"] = enc_el.get("url", "")
            episode["audio_type"] = enc_el.get("type", "audio/mpeg")
            try:
                episode["audio_size"] = int(enc_el.get("length", 0))
            except (ValueError, TypeError):
                episode["audio_size"] = 0
        else:
            episode["audio_url"] = ""
            episode["audio_type"] = ""
            episode["audio_size"] = 0

        if episode["audio_url"]:
            episodes.append(episode)

    return podcast_name, episodes


def filter_episodes(episodes, keywords):
    """Filter episodes by keywords in title and description."""
    if not keywords:
        return episodes

    filtered = []
    for ep in episodes:
        text = (ep["title"] + " " + ep["description"]).lower()
        if any(kw.lower() in text for kw in keywords):
            filtered.append(ep)
    return filtered


def sanitize_filename(name):
    """Create safe filename from episode title."""
    # Remove or replace unsafe characters
    safe = re.sub(r'[<>:"/\\|?*]', "", name)
    safe = re.sub(r"\s+", " ", safe).strip()
    # Limit length
    if len(safe) > 100:
        safe = safe[:100]
    return safe


def format_size(size_bytes):
    """Format byte size to human readable."""
    if size_bytes == 0:
        return "unknown"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def download_episode(audio_url, output_path):
    """Download audio file with progress reporting."""
    req = Request(audio_url, headers={"User-Agent": USER_AGENT})
    response = urlopen(req, timeout=120)

    total_size = response.headers.get("Content-Length")
    total_size = int(total_size) if total_size else None

    downloaded = 0
    chunk_size = 8192

    with open(output_path, "wb") as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                pct = (downloaded / total_size) * 100
                print(f"\r  Downloading: {pct:.0f}% ({format_size(downloaded)})", end="", flush=True)
            else:
                print(f"\r  Downloading: {format_size(downloaded)}", end="", flush=True)

    print()  # newline after progress
    return downloaded


def get_file_extension(audio_type, audio_url):
    """Determine file extension from MIME type or URL."""
    type_map = {
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/x-m4a": ".m4a",
        "audio/mp4": ".m4a",
        "audio/aac": ".aac",
        "audio/ogg": ".ogg",
        "audio/wav": ".wav",
    }
    ext = type_map.get(audio_type, "")
    if not ext:
        # Try from URL
        path = urlparse(audio_url).path
        _, url_ext = os.path.splitext(path)
        ext = url_ext if url_ext else ".mp3"
    return ext


def main():
    parser = argparse.ArgumentParser(
        description="Extract podcast episodes for NotebookLM import"
    )
    parser.add_argument(
        "podcast_url",
        help="Apple Podcasts URL or RSS feed URL",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Comma-separated keywords to filter episodes by title/description",
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=None,
        help="Maximum number of episodes to process (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: ~/Desktop/<podcast_name>/)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List matching episodes without downloading",
    )

    args = parser.parse_args()

    # Step 1: Resolve RSS feed URL
    podcast_name = None
    feed_url = None

    if is_rss_url(args.podcast_url):
        feed_url = args.podcast_url
        print(f"Using RSS feed directly: {feed_url}")
    else:
        podcast_id = extract_podcast_id(args.podcast_url)
        if not podcast_id:
            print("Error: Could not extract podcast ID from URL.")
            print("Expected format: https://podcasts.apple.com/.../id1234567890")
            sys.exit(1)

        print(f"Looking up podcast ID: {podcast_id}")
        feed_url, podcast_name = get_rss_feed_url(podcast_id)
        if not feed_url:
            print("Error: Could not find RSS feed for this podcast.")
            sys.exit(1)
        print(f"Found RSS feed: {feed_url}")

    # Step 2: Parse RSS feed
    print("Fetching RSS feed...")
    try:
        feed_xml = fetch_url(feed_url, timeout=60)
    except (HTTPError, URLError) as e:
        print(f"Error fetching RSS feed: {e}")
        sys.exit(1)

    rss_name, episodes = parse_rss_feed(feed_xml)
    if podcast_name is None:
        podcast_name = rss_name or "podcast"

    print(f"Podcast: {podcast_name}")
    print(f"Total episodes: {len(episodes)}")

    # Step 3: Filter by keywords
    keywords = None
    if args.filter:
        keywords = [k.strip() for k in args.filter.split(",") if k.strip()]
        episodes = filter_episodes(episodes, keywords)
        print(f"Matched episodes ({', '.join(keywords)}): {len(episodes)}")

    if not episodes:
        print("No matching episodes found.")
        sys.exit(0)

    # Step 4: Limit count
    if args.max_episodes and len(episodes) > args.max_episodes:
        episodes = episodes[:args.max_episodes]
        print(f"Limited to: {args.max_episodes} episodes")

    # Step 5: List mode
    if args.list:
        print(f"\n{'='*60}")
        print(f"Matching episodes ({len(episodes)}):")
        print(f"{'='*60}")
        for i, ep in enumerate(episodes, 1):
            size_str = format_size(ep["audio_size"]) if ep["audio_size"] else "unknown size"
            dur_str = ep["duration"] if ep["duration"] else "unknown duration"
            print(f"\n{i}. {ep['title']}")
            print(f"   Date: {ep['pub_date']}")
            print(f"   Duration: {dur_str} | Size: {size_str}")
        sys.exit(0)

    # Step 6: Download episodes
    safe_name = re.sub(r'[<>:"/\\|?*]', "", podcast_name).strip()
    if args.output:
        output_dir = os.path.expanduser(args.output)
    else:
        output_dir = os.path.join(os.path.expanduser("~/Desktop"), safe_name)

    os.makedirs(output_dir, exist_ok=True)

    print(f"\nDownloading {len(episodes)} episodes to: {output_dir}")
    print(f"{'='*60}")

    downloaded_count = 0
    total_bytes = 0

    for i, ep in enumerate(episodes, 1):
        ext = get_file_extension(ep["audio_type"], ep["audio_url"])
        filename = sanitize_filename(ep["title"]) + ext
        filepath = os.path.join(output_dir, filename)

        # Skip existing files
        if os.path.exists(filepath):
            print(f"\n[{i}/{len(episodes)}] Skipping (exists): {filename}")
            downloaded_count += 1
            continue

        print(f"\n[{i}/{len(episodes)}] {ep['title']}")
        try:
            size = download_episode(ep["audio_url"], filepath)
            total_bytes += size
            downloaded_count += 1

            # Warn if file exceeds NotebookLM limit
            if size > 200 * 1024 * 1024:
                print(f"  Warning: File exceeds NotebookLM 200MB limit ({format_size(size)})")

        except Exception as e:
            print(f"  Error: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)

    # Summary
    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"Episodes: {downloaded_count}/{len(episodes)}")
    print(f"Total size: {format_size(total_bytes)}")
    print(f"Output: {output_dir}")
    print(f"\nImport to NotebookLM:")
    print(f"1. Open notebooklm.google.com")
    print(f"2. Click 'Add source' → choose audio files")
    print(f"3. Upload files from: {output_dir}")
    print(f"Note: Max 200MB per file, 50 sources per notebook.")


if __name__ == "__main__":
    main()
