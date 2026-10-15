---
layout: default
title: Malav Naik
---
# Malav Naik

Data analyst and engineer in Dublin, writing about data engineering, generative AI and trust & safety.

{% if site.posts.size == 0 %}
<p class="muted">First posts coming soon.</p>
{% endif %}
<ul class="posts">
{% for post in site.posts %}
  <li><a href="{{ post.url }}">{{ post.title }}</a><br><span class="muted">{{ post.date | date: "%-d %b %Y" }} · {{ post.description }}</span></li>
{% endfor %}
</ul>

Also see my [Employment Permits 2025 dashboard](/permits-2025/), an analysis of Irish employment permits issued to companies.
