---
layout: page
title: arxiv picks
permalink: /arxiv-picks/
---

<h1>My arXiv Paper Collection</h1>
<ul id="paper-list"></ul>

<script>
async function addPaper(arxivId) {
  try {
    const response = await fetch("https://export.arxiv.org/api/query?id_list=" + arxivId);
    const text = await response.text();

    const parser = new DOMParser();
    const xml = parser.parseFromString(text, "application/xml");

    const entry = xml.querySelector("entry");
    if (!entry) {
      console.error("No entry found for", arxivId);
      return;
    }

    const title = entry.querySelector("title").textContent.trim();
    const link = entry.querySelector("id").textContent.trim();

    const li = document.createElement("li");
    li.innerHTML = `<a href="${link}" target="_blank">${title}</a>`;
    document.getElementById("paper-list").appendChild(li);
  } catch (err) {
    console.error("Error fetching arXiv paper:", err);
  }
}

// Example papers
addPaper("2401.16747");
addPaper("2309.67890");
</script>

