---
layout: default
title: Blog
description: Posts by Malav Naik on data engineering, generative AI, trust & safety and building a data career in Dublin.
---
# Blog

Notes on data engineering, generative AI and trust & safety. Browse by [topic]({{ '/blog/topics/' | relative_url }}) or subscribe via [RSS]({{ '/feed.xml' | relative_url }}).

{% if site.posts.size == 0 %}<p class="muted">First posts coming soon.</p>{% endif %}
<ul class="posts">
{% for post in site.posts %}
  {% assign minutes = post.content | number_of_words | divided_by: 200 | at_least: 1 %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a><br><span class="muted">{{ post.date | date: "%-d %b %Y" }} · {{ minutes }} min read · {{ post.description }}</span></li>
{% endfor %}
</ul>
