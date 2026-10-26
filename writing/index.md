---
layout: default
title: Writing
permalink: /writing/
redirect_from: /blog/
wide: true
description: Writing by Malav Naik on data engineering, generative AI, trust & safety and building a data career in Dublin.
---
<p class="label">Writing</p>
<h1>Notes on data, GenAI and trust &amp; safety</h1>
<p class="lead" style="max-width:44rem">Browse by series or by <a href="{{ '/blog/topics/' | relative_url }}">tag</a>, or follow via <a href="{{ '/feed.xml' | relative_url }}">RSS</a>.</p>

<div class="filters" role="group" aria-label="Filter by series">
  <button type="button" class="btn small no-js-hide" data-filter="all" aria-pressed="true">All</button>
  {% for s in site.data.series %}<button type="button" class="btn small no-js-hide" data-filter="{{ s.id }}" aria-pressed="false">{{ s.name }}</button>
  {% endfor %}
</div>
<noscript><p class="small">Series: {% for s in site.data.series %}<a href="{{ '/blog/series/' | append: s.id | append: '/' | relative_url }}">{{ s.name }}</a>{% unless forloop.last %} · {% endunless %}{% endfor %}</p></noscript>

{% if site.posts.size == 0 %}<p class="muted">First posts coming soon.</p>{% endif %}
<h2 class="sr-only">All posts</h2>
<ul class="post-list writing-list">
{% for post in site.posts %}{% assign s = site.data.series | where: "id", post.series | first %}{% assign minutes = post.content | number_of_words | divided_by: 200 | at_least: 1 %}
  <li data-series="{{ post.series }}"><a href="{{ post.url | relative_url }}"><span class="pd">{{ post.date | date: "%-d %b %Y" }}<br>{{ minutes }} min read</span><span><span class="pt">{{ post.title }}</span><span class="pdesc">{{ post.description }}</span>{% if s %}<span class="tag">{{ s.name }}</span>{% endif %}</span></a></li>
{% endfor %}
</ul>
