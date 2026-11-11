---
layout: default
title: Work
permalink: /work/
redirect_from: /projects/
wide: true
description: "Projects by Malav Naik, Data & GenAI Engineer: data engineering, GenAI and AI automation, each with the problem, approach, measured result, stack and code."
---
<p class="label">Work</p>
<h1>Projects, with the numbers to back them</h1>
<p class="lead" style="max-width:44rem">Each case study shows the problem, the approach, the measured result, the stack and the code. Sources for every number are on each project page.</p>
<h2 class="sr-only">All projects</h2>
<ol class="prows" style="margin-top:2rem">
  {%- assign projects = site.projects | sort: "order" -%}
  {%- for p in projects %}
  {% capture n %}{% if forloop.index < 10 %}0{% endif %}{{ forloop.index }}{% endcapture %}{% include project-row.html project=p n=n %}
  {%- endfor %}
</ol>
<p class="small muted" style="margin-top:1.5rem">Want to try them first? The <a href="{{ '/labs/' | relative_url }}">Labs</a> page has the three sandboxes that run in your browser.</p>
