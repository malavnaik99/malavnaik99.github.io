---
layout: default
person_jsonld: true
---
<div class="hero">
  <img src="{{ '/images/malav-naik-portrait.jpg' | relative_url }}" alt="Malav Naik in a navy suit outside the Convention Centre Dublin" width="480" height="480">
  <div>
    <h1>Malav Naik – Data Analyst &amp; Data Engineer (GenAI) in Dublin, Ireland</h1>
  </div>
</div>

Malav Naik is a data analyst and data engineer in Dublin with about 10 years of experience across India and Ireland. He builds data pipelines and AI automation with SQL, Python, Azure and large language models, and writes about data engineering, generative AI and trust & safety.

## Featured projects

<ul class="cards">
{% assign featured = site.projects | where: "featured", true | sort: "order" %}
{% for p in featured %}
  <li class="card">
    <h3><a href="{{ p.url | relative_url }}">{{ p.title }}</a></h3>
    <p>{{ p.summary }}</p>
  </li>
{% endfor %}
</ul>

[All projects →]({{ '/projects/' | relative_url }})

{% include automation-lab.html %}

## Latest posts

<ul class="posts">
{% for post in site.posts limit: 3 %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a><br><span class="muted">{{ post.date | date: "%-d %b %Y" }} · {{ post.description }}</span></li>
{% endfor %}
</ul>

[All posts →]({{ '/blog/' | relative_url }})
