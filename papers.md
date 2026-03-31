---
layout: page
title: arxiv picks
permalink: /arxiv picks/
---

<h1>My arxiv Paper Collection</h1>
<ul id="paper-list"></ul>

<script>
async function addPaper(arxivId) {
  const response = await fetch(`https://export.arxiv.org/api/query?id_list=${2401.16747}`);
  const text = await response.text();
  const parser = new DOMParser();
  const xml = parser.parseFromString(text, "application/xml");
  const title = xml.getElementsByTagName("title")[1].textContent;
  const link = xml.getElementsByTagName("id")[0].textContent;

  const li = document.createElement("li");
  li.innerHTML = `<a href="${link}" target="_blank">${title}</a>`;
  document.getElementById("paper-list").appendChild(li);
}

// Example papers
addPaper("2401.12345");
addPaper("2309.67890");
</script>
