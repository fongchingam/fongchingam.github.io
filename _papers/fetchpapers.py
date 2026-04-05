import feedparser
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from collections import defaultdict

def fetch_arxiv_metadata(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(url)
    if not feed.entries:
        return None
    entry = feed.entries[0]
    pub_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
    return {
        "id": arxiv_id,
        "title": entry.title,
        "authors": [author.name for author in entry.authors],
        "abstract": entry.summary.replace("\n", " "),
        "published": entry.published,
        "year": pub_date.year,
        "month": pub_date.month,
        "link": entry.link
    }

def main():
    # Load existing cache
    cache_path = os.path.join("..", "papers.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            papers = json.load(f)
    else:
        papers = []

    known_ids = {p["id"] for p in papers}

    # Collect new IDs
    new_ids = []
    with open("papers.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            arxiv_id = line.split("/")[-1]
            if arxiv_id not in known_ids:
                new_ids.append(arxiv_id)

    # Fetch new papers in parallel
    if new_ids:
        with ThreadPoolExecutor(max_workers=14) as executor:
            futures = [executor.submit(fetch_arxiv_metadata, pid) for pid in new_ids]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    papers.append(result)

    # Save flat JSON cache
    with open(cache_path, "w") as f:
        json.dump(papers, f, indent=2)

    # Group papers by year/month for Markdown
    grouped = defaultdict(lambda: defaultdict(list))
    for p in papers:
        grouped[p["year"]][p["month"]].append(p)

    md_path = os.path.join("..", "papers.md")
    with open(md_path, "w") as f:
        f.write("""---
layout: page
title: "Arxiv Picks"
permalink: /arxiv-picks/
---
This is my paper collection I find interesting

""")
        for year in sorted(grouped.keys(), reverse=True):
            f.write(f"# {year}\n\n")
            for month in sorted(grouped[year].keys(), reverse=True):
                month_name = datetime(year, month, 1).strftime("%B")
                f.write(f"## {month_name} {year}\n\n")
                for p in grouped[year][month]:
                    f.write(f"### [{p['title']}]({p['link']})\n")
                    f.write(f"**Authors:** {', '.join(p['authors'])}\n\n")
                    f.write(f"**Published:** {p['published']}\n\n")
                    f.write(f"{p['abstract']}\n\n---\n\n")

if __name__ == "__main__":
    main()

