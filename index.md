---
layout: default
wide: true
---
<section class="hero">
  <img src="{{ '/images/malav-naik-portrait.jpg' | relative_url }}" alt="Malav Naik in a navy suit outside the Convention Centre Dublin" width="480" height="480" fetchpriority="high">
  <div>
    <p class="eyebrow">Dublin, Ireland</p>
    <h1>Malav Naik</h1>
    <p class="lead">Data Engineer, GenAI &amp; AI Automation</p>
    <p>Malav Naik is a data analyst and data engineer in Dublin with about 10 years of experience across India and Ireland. He builds data pipelines and AI automation with SQL, Python, Azure and large language models, and writes about data engineering, generative AI and trust &amp; safety.</p>
    <ul class="proof">
      <li><strong>About 10 years in data</strong> across India and Ireland, from SQL Server and SSIS to Azure</li>
      <li><strong>MSc in Data Analytics</strong> from National College of Ireland</li>
      <li><strong>{{ site.projects.size }} public projects</strong> with code, measured results and write-ups</li>
    </ul>
    <p class="actions"><a class="btn btn-primary" href="{{ '/blog/' | relative_url }}">Read the blog</a> <a class="btn" href="{{ '/projects/' | relative_url }}">View projects</a></p>
  </div>
</section>

<div class="section-head"><h2>Latest posts</h2><a href="{{ '/blog/' | relative_url }}">All posts</a></div>
<ul class="grid">{% for post in site.posts limit: 3 %}{% include post-card.html post=post %}{% endfor %}</ul>

<div class="section-head"><h2>Featured projects</h2><a href="{{ '/projects/' | relative_url }}">All projects</a></div>
<ul class="grid">{% assign featured = site.projects | where: "featured", true | sort: "order" %}{% for p in featured limit: 3 %}{% include project-card.html project=p %}{% endfor %}</ul>

{% include automation-lab.html %}
