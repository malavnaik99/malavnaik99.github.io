---
layout: default
title: Projects
description: Projects by Malav Naik – AI automation, data engineering and analytics, each with how it works, a demo and the code.
---
# Projects

What I've built, with how it works, a demo and the code.

<ul class="cards">
{% assign projects = site.projects | sort: "order" %}
{% for p in projects %}
  <li class="card">
    <h3><a href="{{ p.url | relative_url }}">{{ p.title }}</a></h3>
    <p>{{ p.summary }}</p>
    {% if p.tech %}<ul class="chips">{% for t in p.tech limit: 4 %}<li>{{ t }}</li>{% endfor %}</ul>{% endif %}
  </li>
{% endfor %}
</ul>
