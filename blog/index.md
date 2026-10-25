---
layout: default
title: Blog
wide: true
description: Posts by Malav Naik on data engineering, generative AI, trust & safety and building a data career in Dublin.
---
<h1>Blog</h1>
<p class="lead">Notes on data engineering, generative AI and trust &amp; safety. Browse a series, the <a href="{{ '/blog/topics/' | relative_url }}">tags</a>, or subscribe via <a href="{{ '/feed.xml' | relative_url }}">RSS</a>.</p>

<div class="filters" role="group" aria-label="Filter by series">
  <button type="button" class="btn small no-js-hide" data-filter="all" aria-pressed="true">All</button>
  {% for s in site.data.series %}<button type="button" class="btn small no-js-hide" data-filter="{{ s.id }}" aria-pressed="false">{{ s.name }}</button>
  {% endfor %}
</div>
<noscript><p class="small">Series: {% for s in site.data.series %}<a href="{{ '/blog/series/' | append: s.id | append: '/' | relative_url }}">{{ s.name }}</a>{% unless forloop.last %} · {% endunless %}{% endfor %}</p></noscript>

{% if site.posts.size == 0 %}<p class="muted">First posts coming soon.</p>{% endif %}
<h2 class="sr-only">All posts</h2>
<ul class="grid">{% for post in site.posts %}{% include post-card.html post=post %}{% endfor %}</ul>
