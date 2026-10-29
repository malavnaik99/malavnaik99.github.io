---
layout: default
title: Work
permalink: /work/
redirect_from: /projects/
wide: true
description: Projects by Malav Naik, Data & GenAI Engineer: data engineering, GenAI and AI automation, each with the problem, approach, measured result, stack and code.
---
<p class="label">Work</p>
<h1>Projects, with the numbers to back them</h1>
<p class="lead" style="max-width:44rem">Each case study shows the problem, the approach, the measured result, the stack and the code. Sources for every number are on each project page.</p>
<h2 class="sr-only">All projects</h2>
<ul class="grid" style="margin-top:2rem">{% assign projects = site.projects | sort: "order" %}{% for p in projects %}{% include project-card.html project=p %}{% endfor %}</ul>
