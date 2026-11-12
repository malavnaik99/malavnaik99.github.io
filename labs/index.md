---
layout: default
title: Labs
permalink: /labs/
wide: true
description: "Three sandboxes by Malav Naik, Data & GenAI Engineer, that run in your browser: a content moderation threshold, keyword vs vector search over the EU Digital Services Act, and SQL over a tested Dublin bikes data pipeline."
---
<p class="label">Labs</p>
<h1>Three sandboxes you can use right here</h1>
<p class="lead" style="max-width:44rem">Real results from my projects, in your browser. Each sandbox keeps its settings in the page address, so <b>Copy link to this view</b> shares exactly what you see.</p>
<ul class="labs-index">
  <li><a href="#sandbox-moderation">Content moderation threshold</a></li>
  <li><a href="#sandbox-dsa">Keyword vs vector search</a></li>
  <li><a href="#sql">SQL on the Dublin bikes pipeline</a></li>
</ul>

<section class="lab" aria-labelledby="lab-moderation">
  <h2 id="lab-moderation">Content moderation: where to draw the line</h2>
  <p class="muted">From the <a href="{{ '/projects/moderation-classifier/' | relative_url }}">content moderation classifier case study</a>.</p>
  {% include sandbox-moderation.html %}
</section>

<section class="lab" aria-labelledby="lab-dsa">
  <h2 id="lab-dsa">Ask the EU Digital Services Act: keyword vs vector search</h2>
  <p class="muted">From the <a href="{{ '/projects/ask-the-dsa/' | relative_url }}">Ask the DSA case study</a>.</p>
  {% include sandbox-dsa.html %}
</section>

<section class="lab" aria-labelledby="lab-sql">
  <h2 id="lab-sql">Dublin bikes: query the pipeline's tables</h2>
  <p class="muted">From the <a href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}">Dublin bikes data pipeline case study</a>.</p>
  {% include sandbox-sql.html %}
</section>
