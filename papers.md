---
layout: page
title: "Arxiv Picks"
permalink: /arxiv-picks/
---

<h1>My arXiv Paper Collection</h1>

<input type="text" id="arxiv-input" placeholder="Enter arXiv ID (e.g. 2401.16747)">
<button onclick="addPaper(document.getElementById('arxiv-input').value)">Add Paper</button>

<ul id="paper-list"></ul>

<script>
async function addPaper(arxivId) {
  if (!arxivId) return;

  try {
    const response = await fetch("https://export.arxiv.org/api/query?id_list=" + arxivId);
    const text = await response.text();

    const parser = new DOMParser();
    const xml = parser.parseFromString(text, "application/xml");
    const entry = xml.querySelector("entry");

    if (!entry) {
      alert("No paper found for ID " + arxivId);
      return;
    }

    const title = entry.querySelector("title").textContent.trim();
    const link = entry.querySelector("id").textContent.trim();
    const authors = Array.from(entry.querySelectorAll("author > name"))
                         .map(el => el.textContent.trim())
                         .join(", ");
    const summary = entry.querySelector("summary").textContent.trim();

    const li = document.createElement("li");
    li.innerHTML = `
      <strong><a href="${link}" target="_blank">${title}</a></strong><br>
      <em>${authors}</em><br>
      <button onclick="this.nextElementSibling.style.display =
        this.nextElementSibling.style.display==='none' ? 'block' : 'none'">
        Toggle Abstract
      </button>
      <div style="display:none; margin-top:0.5em;">${summary}</div>
    `;
    document.getElementById("paper-list").appendChild(li);
  } catch (err) {
    console.error("Error fetching arXiv paper:", err);
  }
}

// Example papers
addPaper("2401.16747");
addPaper("2309.67890");
</script>

