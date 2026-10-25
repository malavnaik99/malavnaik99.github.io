---
layout: default
title: Projects
wide: true
description: Projects by Malav Naik – AI automation, data engineering and analytics, each with the problem, approach, result, stack and code.
---
<h1>Projects</h1>
<p class="lead">What I've built: the problem, the approach, the measured result, and the code.</p>
<ul class="grid">{% assign projects = site.projects | sort: "order" %}{% for p in projects %}{% include project-card.html project=p %}{% endfor %}</ul>
