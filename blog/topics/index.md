---
layout: default
title: Blog topics
description: Malav Naik's blog posts grouped by series and by tag.
---
# Blog topics

{% assign series = site.posts | group_by: "series" %}
## Series
{% for s in series %}{% if s.name != "" %}
<h3 id="series-{{ s.name }}">{{ s.name | replace: "-", " " | capitalize }}</h3>
<ul class="posts">{% for p in s.items %}<li><a href="{{ p.url | relative_url }}">{{ p.title }}</a></li>{% endfor %}</ul>
{% endif %}{% endfor %}

## Tags
{% assign tags = site.tags | sort %}
{% for t in tags %}
<h3 id="tag-{{ t[0] }}">#{{ t[0] }}</h3>
<ul class="posts">{% for p in t[1] %}<li><a href="{{ p.url | relative_url }}">{{ p.title }}</a></li>{% endfor %}</ul>
{% endfor %}
