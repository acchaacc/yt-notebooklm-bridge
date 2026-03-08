#!/usr/bin/env python3
"""
Extract podcast episode URLs from Apple Podcasts and save as .md file.
For Apple Podcasts URLs: uses RSS feed for full episode list + iTunes API for
Apple Podcasts page URLs (hybrid approach, no 200 episode limit on filtering).
For RSS feed URLs: outputs audio URLs from enclosures.
Supports keyword filtering, episode limiting, and direct RSS feed URLs.
Zero external dependencies — uses only Python stdlib.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ITUNES_LOOKUP_BASE = "https://itunes.apple.com/lookup"
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


def is_rss_url(url):
    """Check if URL looks like an RSS feed (not Apple Podcasts)."""
    parsed = urlparse(url)
    return "podcasts.apple.com" not in parsed.netloc


def get_itunes_url_map(podcast_id):
    """Build title → Apple Podcasts URL mapping from iTunes Lookup API.

    Returns (podcast_name, {normalized_title: apple_podcasts_url}).
    """
    url = f"{ITUNES_LOOKUP_BASE}?id={podcast_id}&entity=podcastEpisode&limit=200"
    data = json.loads(fetch_url(url, timeout=60))
    results = data.get("results", [])

    podcast_name = None
    url_map = {}

    for result in results:
        wrapper_type = result.get("wrapperType", "")
        kind = result.get("kind", "")

        # Podcast info comes as wrapperType "track" with kind "podcast"
        if kind == "podcast" and wrapper_type == "track":
            podcast_name = result.get("collectionName") or result.get("trackName", "podcast")
            continue

        if wrapper_type == "podcastEpisode":
            title = result.get("trackName", "")
            apple_url = result.get("trackViewUrl", "")
            if title and apple_url:
                url_map[title.strip()] = apple_url

    return podcast_name, url_map


def get_rss_feed_url(podcast_id):
    """Get RSS feed URL from iTunes Lookup API."""
    url = f"{ITUNES_LOOKUP_BASE}?id={podcast_id}&entity=podcast"
    data = json.loads(fetch_url(url))
    results = data.get("results", [])
    if not results:
        return None, None
    result = results[0]
    return result.get("feedUrl"), result.get("collectionName", "podcast")


def parse_rss_feed(feed_xml):
    """Parse RSS feed XML and extract episode data."""
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")
    if channel is None:
        return None, []

    podcast_name = ""
    title_el = channel.find("title")
    if title_el is not None and title_el.text:
        podcast_name = title_el.text.strip()

    episodes = []
    itunes_ns = "http://www.itunes.com/dtds/podcast-1.0.dtd"

    for item in channel.findall("item"):
        episode = {}

        title_el = item.find("title")
        episode["title"] = title_el.text.strip() if title_el is not None and title_el.text else "Untitled"

        desc = ""
        for tag in ["description", f"{{{itunes_ns}}}summary"]:
            el = item.find(tag)
            if el is not None and el.text:
                desc = el.text.strip()
                break
        episode["description"] = desc

        pub_el = item.find("pubDate")
        episode["pub_date"] = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

        dur_el = item.find(f"{{{itunes_ns}}}duration")
        episode["duration"] = dur_el.text.strip() if dur_el is not None and dur_el.text else ""

        enc_el = item.find("enclosure")
        if enc_el is not None:
            episode["url"] = enc_el.get("url", "")
        else:
            episode["url"] = ""

        if episode["url"]:
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


def save_as_markdown(urls, output_path):
    """Save URLs as markdown file with space separation."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(" ".join(urls))
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract podcast episode URLs for NotebookLM import"
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
        help="Output file path (default: ~/Desktop/<podcast_name>_notebooklm.md)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List matching episodes without saving",
    )

    args = parser.parse_args()

    podcast_name = None
    episodes = []

    if is_rss_url(args.podcast_url):
        # RSS feed: parse and extract audio URLs
        print(f"Using RSS feed directly: {args.podcast_url}")
        try:
            feed_xml = fetch_url(args.podcast_url, timeout=60)
        except (HTTPError, URLError) as e:
            print(f"Error fetching RSS feed: {e}")
            sys.exit(1)

        podcast_name, episodes = parse_rss_feed(feed_xml)
        if not podcast_name:
            podcast_name = "podcast"
        print(f"Podcast: {podcast_name}")
        print(f"Total episodes: {len(episodes)}")
        print("Mode: audio URLs from RSS feed")
    else:
        # Apple Podcasts URL: hybrid approach
        # 1. Get RSS feed for complete episode list (unlimited)
        # 2. Get iTunes API data for Apple Podcasts URL mapping (up to 200)
        # 3. Filter from RSS, map to Apple Podcasts URLs
        podcast_id = extract_podcast_id(args.podcast_url)
        if not podcast_id:
            print("Error: Could not extract podcast ID from URL.")
            print("Expected format: https://podcasts.apple.com/.../id1234567890")
            sys.exit(1)

        print(f"Looking up podcast ID: {podcast_id}")

        # Step 1: Get RSS feed URL and fetch all episodes
        try:
            feed_url, itunes_name = get_rss_feed_url(podcast_id)
        except (HTTPError, URLError) as e:
            print(f"Error looking up podcast: {e}")
            sys.exit(1)

        if not feed_url:
            print("Error: Could not find RSS feed for this podcast.")
            sys.exit(1)

        print(f"Fetching RSS feed: {feed_url}")
        try:
            feed_xml = fetch_url(feed_url, timeout=60)
        except (HTTPError, URLError) as e:
            print(f"Error fetching RSS feed: {e}")
            sys.exit(1)

        podcast_name, episodes = parse_rss_feed(feed_xml)
        if not podcast_name:
            podcast_name = itunes_name or "podcast"
        print(f"Podcast: {podcast_name}")
        print(f"Total episodes from RSS: {len(episodes)}")

        # Step 2: Get Apple Podcasts URL mapping from iTunes API
        print("Fetching Apple Podcasts URLs from iTunes API...")
        try:
            _, url_map = get_itunes_url_map(podcast_id)
        except (HTTPError, URLError) as e:
            print(f"Warning: Could not fetch iTunes data: {e}")
            url_map = {}

        print(f"Apple Podcasts URLs available: {len(url_map)} (iTunes API max 200)")

        # Step 3: Replace audio URLs with Apple Podcasts URLs where possible
        mapped = 0
        unmapped = 0
        for ep in episodes:
            apple_url = url_map.get(ep["title"])
            if apple_url:
                ep["url"] = apple_url
                mapped += 1
            else:
                unmapped += 1

        print(f"URL mapping: {mapped} mapped, {unmapped} unmapped (older episodes)")
        print("Mode: Apple Podcasts episode URLs")

    # Filter by keywords
    keywords = None
    if args.filter:
        keywords = [k.strip() for k in args.filter.split(",") if k.strip()]
        episodes = filter_episodes(episodes, keywords)
        print(f"Matched episodes ({', '.join(keywords)}): {len(episodes)}")

    if not episodes:
        print("No matching episodes found.")
        sys.exit(0)

    # For Apple Podcasts mode: only keep episodes with Apple Podcasts URLs
    if not is_rss_url(args.podcast_url):
        before = len(episodes)
        episodes = [ep for ep in episodes if "podcasts.apple.com" in ep["url"]]
        skipped = before - len(episodes)
        if skipped:
            print(f"  Skipped {skipped} older episodes without Apple Podcasts URLs")
            print(f"  Kept {len(episodes)} episodes with Apple Podcasts URLs")

    # Limit count
    if args.max_episodes and len(episodes) > args.max_episodes:
        episodes = episodes[:args.max_episodes]
        print(f"Limited to: {args.max_episodes} episodes")

    # List mode
    if args.list:
        print(f"\n{'='*60}")
        print(f"Matching episodes ({len(episodes)}):")
        print(f"{'='*60}")
        for i, ep in enumerate(episodes, 1):
            dur_str = ep["duration"] if ep["duration"] else "unknown duration"
            url_type = "Apple Podcasts" if "podcasts.apple.com" in ep["url"] else "audio"
            print(f"\n{i}. {ep['title']}")
            print(f"   Date: {ep['pub_date']}")
            print(f"   Duration: {dur_str} | URL type: {url_type}")
        sys.exit(0)

    # Save URLs to .md file
    urls = [ep["url"] for ep in episodes]

    safe_name = re.sub(r'[<>:"/\\|?*]', "", podcast_name).strip()
    safe_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in safe_name
    )

    if args.output:
        output_path = os.path.expanduser(args.output)
    else:
        desktop = os.path.expanduser("~/Desktop")
        output_path = os.path.join(desktop, f"{safe_name}_notebooklm.md")

    save_as_markdown(urls, output_path)

    print(f"\nSaved to: {output_path}")
    print(f"Total URLs: {len(urls)}")
    print(f"\nYou can now import these as sources in NotebookLM.")


if __name__ == "__main__":
    main()
