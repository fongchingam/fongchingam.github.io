import requests
from bs4 import BeautifulSoup
import json, os, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from collections import defaultdict

def sanitize_arxiv_id(line):
    line = line.strip()
    if not line:
        return None
    # Modern IDs
    match = re.search(r'(\d{4}\.\d{4,5})', line)
    if match:
        return match.group(1)
    # Legacy IDs
    match = re.search(r'([a-z\-]+/\d{7})', line)
    if match:
        return match.group(1)
    return None

def fetch_from_html(arxiv_id):
    url = f"https://arxiv.org/abs/{arxiv_id}"
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        print(f"[DEBUG] Request error for {arxiv_id}: {e}")
        return None
    if resp.status_code != 200:
        print(f"[DEBUG] Request failed for {arxiv_id} with status {resp.status_code}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    title_el = soup.find("h1", class_="title")
    title = title_el.get_text(strip=True).replace("Title:", "") if title_el else ""

    authors_div = soup.find("div", class_="authors")
    authors = [a.get_text(strip=True) for a in authors_div.find_all("a")] if authors_div else []

    abstract_block = soup.find("blockquote", class_="abstract")
    abstract = abstract_block.get_text(strip=True).replace("Abstract:", "") if abstract_block else ""

    history_div = soup.find("div", class_="submission-history")
    published = history_div.get_text(" ", strip=True) if history_div else ""

    # Try to parse year/month from submission history text
    year, month = None, None
    try:
        # Example: "Submitted on 2 Apr 2026"
        m = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", published)
        if m:
            pub_date = datetime.strptime(m.group(1), "%d %b %Y")
            year, month = pub_date.year, pub_date.month
    except Exception:
        pass

    return {
        "id": arxiv_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published,
        "year": year,
        "month": month,
        "link": url
    }

def main():
    cache_path = os.path.join("..", "papers.json")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            papers = json.load(f)
    else:
        papers = []

    print(f"[DEBUG] Loaded cache with {len(papers)} papers")

    known_ids = {p["id"] for p in papers}
    new_ids = []
    with open("newpapers.txt") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            arxiv_id = sanitize_arxiv_id(line)
            if arxiv_id and arxiv_id not in known_ids:
                new_ids.append(arxiv_id)

    print(f"[DEBUG] Found {len(new_ids)} new IDs to fetch")

    failed_ids = []
    if new_ids:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {executor.submit(fetch_from_html, pid): pid for pid in new_ids}
            for future in as_completed(future_to_id):
                pid = future_to_id[future]
                result = future.result()
                if result:
                    papers.append(result)
                else:
                    failed_ids.append(pid)

    print(f"[DEBUG] Total papers after update: {len(papers)}")
    print(f"[DEBUG] Failed to fetch {len(failed_ids)} papers")
    if failed_ids:
        print("[DEBUG] Example failed IDs:", failed_ids[:10])

    # Save JSON cache
    with open(cache_path, "w") as f:
        json.dump(papers, f, indent=2)

    # Group papers by year/month for Markdown
    grouped = defaultdict(lambda: defaultdict(list))
    for p in papers:
        if p.get("year") and p.get("month"):
            grouped[p["year"]][p["month"]].append(p)

    md_path = os.path.join("..", "papers.md")
    with open(md_path, "w") as f:
        f.write("""---
layout: page
title: "Arxiv Picks"
permalink: /arxiv-picks/
---

I check arxiv daily to collect papers I find interesting, relevant to my research, or have funny titles. 

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

    total_grouped = sum(len(grouped[y][m]) for y in grouped for m in grouped[y])
    print(f"[DEBUG] Markdown written with {total_grouped} papers grouped")

if __name__ == "__main__":
    main()

