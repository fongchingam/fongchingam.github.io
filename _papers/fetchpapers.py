import feedparser
import json

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
    weeks = {}
    current_week = None

    with open("papers.txt") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# Week"):
                current_week = line.lstrip("# ").strip()
                weeks[current_week] = []
            else:
                arxiv_id = line.split("/")[-1]
                meta = fetch_arxiv_metadata(arxiv_id)
                if meta and current_week:
                    weeks[current_week].append(meta)

    # Save JSON grouped by week
    with open("papers.json", "w") as f:
        json.dump(weeks, f, indent=2)

    # Save Markdown grouped by week
    with open("papers.md", "w") as f:
        for week, papers in weeks.items():
            f.write(f"## Papers from {week}\n\n")
            for p in papers:
                f.write(f"### [{p['title']}]({p['link']})\n")
                f.write(f"**Authors:** {', '.join(p['authors'])}\n\n")
                f.write(f"**Published:** {p['published']}\n\n")
                f.write(f"{p['abstract']}\n\n---\n\n")

if __name__ == "__main__":
    main()

