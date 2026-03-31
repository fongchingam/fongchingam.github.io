---
layout: page
title: arxiv picks
permalink: /arxiv-picks/
---

<h1>My arXiv Paper Collection</h1>
<ul id="paper-list"></ul>

<script>
async function addPaper(arxivId) {
  // Use the argument instead of hardcoding
  const response = await fetch(`https://export.arxiv.org/api/query?id_list=${arxivId}`);
  const text = await response.text();

  // Parse the Atom XML
  const parser = new DOMParser();
  const xml = parser.parseFromString(text, "application/xml");

  // The first <entry> contains the paper info
  const entry = xml.getElementsByTagName("entry")[0];
  if (!entry) {
    console.error("No entry found for", arxivId);
    return;
  }

  const title = entry.getElementsByTagName("title")[0].textContent.trim();
  const link = entry.getElementsByTagName("id")[0].textContent.trim();

  // Add to the list
  const li = document.createElement("li");
  li.innerHTML = `<a href="${link}" target="_blank">${title}</a>`;
  document.getElementById("paper-list").appendChild(li);
}

// Example papers
addPaper("2401.12345");
addPaper("2309.67890");
</script>


