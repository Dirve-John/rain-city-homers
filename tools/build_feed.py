#!/usr/bin/env python3
"""Rebuild feed.xml for Rain City Homers from episodes.json.

Usage: build_feed.py <site_dir>
episodes.json: list of {"file", "title", "description", "pub_date" (RFC 2822), "duration_sec"}
Keeps only the newest MAX_EPISODES entries (and deletes older MP3s).
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

BASE_URL = "https://dirve-john.github.io/rain-city-homers"
MAX_EPISODES = 10
SHOW = {
    "title": "Rain City Homers",
    "author": "Cal & Rusty",
    "description": ("Gonzaga hoops, the Seahawks, the Mariners and Husky football, "
                    "with unapologetic homers Cal and Rusty, plus the national stories worth your time. "
                    "New episodes Monday and Friday mornings."),
}


def main(site):
    site = Path(site)
    eps = json.loads((site / "episodes.json").read_text())
    eps.sort(key=lambda e: e["file"], reverse=True)
    keep, drop = eps[:MAX_EPISODES], eps[MAX_EPISODES:]
    for e in drop:
        (site / "episodes" / e["file"]).unlink(missing_ok=True)
    (site / "episodes.json").write_text(json.dumps(keep, indent=2))

    items = []
    for e in keep:
        size = (site / "episodes" / e["file"]).stat().st_size
        url = f"{BASE_URL}/episodes/{e['file']}"
        d = int(e["duration_sec"])
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(e['description'])}</description>
      <enclosure url="{url}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(e['file'])}</guid>
      <pubDate>{e['pub_date']}</pubDate>
      <itunes:duration>{d // 3600:02d}:{d % 3600 // 60:02d}:{d % 60:02d}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW['title']}</title>
    <link>{BASE_URL}/</link>
    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>en-us</language>
    <description>{escape(SHOW['description'])}</description>
    <itunes:author>{escape(SHOW['author'])}</itunes:author>
    <itunes:summary>{escape(SHOW['description'])}</itunes:summary>
    <itunes:image href="{BASE_URL}/cover.png"/>
    <itunes:category text="Sports"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (site / "feed.xml").write_text(feed)
    print(f"feed.xml written with {len(keep)} episodes")


if __name__ == "__main__":
    main(sys.argv[1])
