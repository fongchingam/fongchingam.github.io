import feedparser
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_arxiv_metadata(arxiv_id):
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(url)
    if not feed.entries:
        return None
    entry = feed.entries[0]
    return {
        "id": arxiv_id,
        "title": entry.title,
        "authors": [author.name for author in entry.authors],
        "abstract": entry.summary.replace("\n", " "),
        "published": entry.published,
        "link": entry.link
    }

def main():
    # Read paper IDs from papers.txt
    paper_ids = []
    with open("papers.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # skip week headers
                continue
            arxiv_id = line.split("/")[-1]
            paper_ids.append(arxiv_id)

    papers = []

    # Fetch metadata in parallel
    with ThreadPoolExecutor(max_workers=14) as executor:
        future_to_id = {executor.submit(fetch_arxiv_metadata, pid): pid for pid in paper_ids}
        for future in as_completed(future_to_id):
            result = future.result()
            if result:
                papers.append(result)

    # Save JSON one directory above
    with open(os.path.join("..", "papers.json"), "w") as f:
        json.dump(papers, f, indent=2)

    # Save Markdown one directory above
    with open(os.path.join("..", "papers.md"), "w") as f:
        # Write YAML front matter + intro
        f.write("""---
layout: page
title: "Arxiv Picks"
permalink: /arxiv-picks/
---
This is my paper collection I find interesting

""")
        # Write paper entries
        for p in papers:
            f.write(f"### [{p['title']}]({p['link']})\n")
            f.write(f"**Authors:** {', '.join(p['authors'])}\n\n")
            f.write(f"**Published:** {p['published']}\n\n")
            f.write(f"{p['abstract']}\n\n---\n\n")

if __name__ == "__main__":
    main()

