---
layout: default
# Same as identity.json "title" (checked by scripts/check_identity.py); makes the home page title exactly that.
title: "Malav Naik | Data & GenAI Engineer | Dublin, Ireland"
wide: true
description: "Malav Naik, Data & GenAI Engineer in Dublin, Ireland: tested data pipelines with dbt and DuckDB, GenAI and AI automation, and writing on data engineering and trust & safety."
---
{% assign lab = site.data.automation %}

<section class="hero" aria-labelledby="hero-title">
  <div class="sky" aria-hidden="true"><span class="stars"></span></div>
  <div class="hero-inner">
    <div class="hero-copy">
      <p class="label pill">{{ site.data.identity.job_title | escape }} · {{ site.data.identity.location.city }}, {{ site.data.identity.location.country }}</p>
      <h1 id="hero-title">I build data pipelines and GenAI systems, and prove they work.</h1>
      <p class="sub">About 10 years in data, from SSIS pipelines and an Azure SQL migration at S&amp;P Global Market Intelligence to dbt, DuckDB and LLM tools today. Every project here shows its code and measured results.</p>
      <p class="actions"><a class="btn btn-accent" href="{{ '/work/' | relative_url }}">See the work</a> <a class="btn" href="{{ '/resume/' | relative_url }}">Résumé</a></p>
      <p class="open-to">{{ site.data.identity.open_to | escape }}</p>
    </div>
    {% include hero-demo.html %}
  </div>
</section>

{% capture signals %}
  <li><span class="k">pipeline</span> <span data-pipeline><span class="dot" aria-hidden="true"></span><span class="status">runs every 15 min</span></span></li>
  <li><b>0.957</b> <span class="k">ROC-AUC, content moderation model</span></li>
  <li><b>14</b> <span class="k">automatic data tests on every run</span></li>
  <li><b>€0</b> <span class="k">monthly cost</span></li>
  <li><span class="k">Ask the EU Digital Services Act</span> <b>84% top-3 hit rate</b></li>
  {% if lab %}<li><span class="k">blog bot</span> <b>{{ lab.posts_published }}</b> <span class="k">posts published</span></li>
  <li><b>{{ lab.posts_queued }}</b> <span class="k">queued</span></li>{% endif %}
  <li>{% include cadentiq-cta.html variant="link" placement="ticker" %}</li>
  {% for post in site.posts limit: 1 %}<li><span class="k">{{ post.date | date: "%-d %b %Y" }}</span> <b>{{ post.title }}</b></li>{% endfor %}
{% endcapture %}
<section class="ticker" aria-labelledby="ticker-title">
  <p class="ticker-label" id="ticker-title"><span class="dot" aria-hidden="true"></span>Live signals</p>
  <div class="ticker-view"><div class="ticker-track"><ul>{{ signals }}</ul><ul aria-hidden="true">{{ signals | replace: '<a ', '<a tabindex="-1" ' }}</ul></div></div>
</section>

{%- comment -%} Four standing facts; each figure is sourced in docs/METRIC_SOURCES.md and links to its project. {%- endcomment %}
<ul class="proof" aria-label="Proof in numbers">
  <li><a href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}"><span class="num num-status" data-pipeline><span class="dot" aria-hidden="true"></span><span class="status">runs every 15 min</span></span><span class="what">Dublin bikes data pipeline</span></a></li>
  <li><a href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}"><span class="num">14</span><span class="what">automatic data tests on every pipeline run</span></a></li>
  <li><a href="{{ '/projects/moderation-classifier/' | relative_url }}"><span class="num">0.957</span><span class="what">ROC-AUC, content moderation model</span></a></li>
  <li><a href="{{ '/projects/ask-the-dsa/' | relative_url }}"><span class="num">84%</span><span class="what">top-3 hit rate, Ask the EU Digital Services Act</span></a></li>
</ul>

<div class="ask palette" id="ask" role="region" aria-labelledby="ask-title">
  <p class="label" id="ask-title">Ask about my work</p>
  <form id="ask-form">
    <label class="sr-only" for="ask-input">Your question</label>
    <input id="ask-input" type="text" placeholder="e.g. How do you test a data pipeline?" autocomplete="off">
    <button class="btn btn-accent" type="submit">Ask</button>
  </form>
  <p class="ask-status small" id="ask-status" role="status"></p>
  <ul class="ask-results" id="ask-results" aria-label="Pages that match your question"></ul>
  <ul class="examples" aria-label="Example questions">
    <li><button type="button" data-answer="ans-1" aria-expanded="false" aria-controls="ans-1">What's your strongest project?</button></li>
    <li><button type="button" data-answer="ans-2" aria-expanded="false" aria-controls="ans-2">How do you build data pipelines?</button></li>
    <li><button type="button" data-answer="ans-3" aria-expanded="false" aria-controls="ans-3">What's your background?</button></li>
  </ul>
  <div class="answer" id="ans-1" hidden>
    <p>A content moderation classifier trained on 1.8 million public comments. The DistilBERT model reached a ROC-AUC of 0.957, and I checked how often harmless comments mentioning each identity group were wrongly flagged.</p>
    <p class="source">source: <a href="{{ '/projects/moderation-classifier/' | relative_url }}">/projects/moderation-classifier/</a></p>
  </div>
  <div class="answer" id="ans-2" hidden>
    <p>Small and append-only first: the Dublin bikes collector saves every station every 15 minutes. dbt on DuckDB then builds a tested star schema with 14 automatic data checks, published as Parquet on Hugging Face, for €0 a month.</p>
    <p class="source">source: <a href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}">/projects/dublin-bikes-pipeline/</a></p>
  </div>
  <div class="answer" id="ans-3" hidden>
    <p>About 10 years in data: Data Analyst at Bright Info Solutions, then Data Analyst &amp; ETL Developer at S&amp;P Global Market Intelligence, where an Azure SQL migration cut infrastructure costs by about 25%. Then an MSc in Data Analytics at National College of Ireland, and now platform integrity work at Accenture for a global technology client.</p>
    <p class="source">source: <a href="{{ '/about/' | relative_url }}">/about/</a></p>
  </div>
</div>

<section class="section" id="work" aria-labelledby="work-title">
  <p class="label"><b>01</b> / Selected work</p>
  <div class="section-head"><h2 id="work-title">Projects, each with its own numbers</h2><a href="{{ '/work/' | relative_url }}">All projects →</a></div>
  <ol class="prows">
    {%- assign projects = site.projects | where: "home", true | sort: "order" -%}
    {%- for p in projects %}
    {% capture n %}{% if forloop.index < 10 %}0{% endif %}{{ forloop.index }}{% endcapture %}{% include project-row.html project=p n=n %}
    {%- endfor %}
  </ol>
</section>

<section class="section" id="toolkit" aria-labelledby="toolkit-title">
  <p class="label"><b>02</b> / Toolkit</p>
  <h2 id="toolkit-title">Tools I've used in real projects</h2>
  <div class="toolkit">
  <div class="tabs">
    <div class="tablist" role="tablist" aria-label="Toolkit areas">
      {% for area in site.data.toolkit %}<button type="button" role="tab" id="tab-{{ area.id }}" aria-controls="panel-{{ area.id }}" aria-selected="{% if forloop.first %}true{% else %}false{% endif %}"{% unless forloop.first %} tabindex="-1"{% endunless %}><span class="mono">0{{ forloop.index }}</span>{{ area.name }}</button>
      {% endfor %}
    </div>
    <div>
      {% for area in site.data.toolkit %}<div role="tabpanel" id="panel-{{ area.id }}" aria-labelledby="tab-{{ area.id }}" tabindex="0"{% unless forloop.first %} hidden{% endunless %}>
        <h3 class="sr-only">{{ area.name }}</h3>
        <ul class="tools">{% for t in area.tools %}<li>{{ t }}</li>{% endfor %}</ul>
      </div>
      {% endfor %}
    </div>
  </div>
  {% include constellation.html %}
  </div>
</section>

<section class="section journey-section" id="journey" aria-labelledby="journey-title">
  <p class="label"><b>03</b> / From Surat to Dublin</p>
  <h2 id="journey-title">Ten years, two countries, one thread: data</h2>
  <figure class="photo-card">
    <img src="{{ '/images/malav-naik-portrait.jpg' | relative_url }}" alt="Malav Naik in a navy suit outside the Convention Centre Dublin" width="480" height="480" loading="lazy" decoding="async">
    <dl class="readout">
      <dt>name</dt><dd>Malav Naik</dd>
      <dt>based</dt><dd>Dublin, Ireland</dd>
      <dt>focus</dt><dd>data pipelines · GenAI · AI automation</dd>
      <dt>pipeline</dt><dd data-pipeline><span class="dot" aria-hidden="true"></span><span class="status">runs every 15 min</span></dd>
    </dl>
  </figure>
  {% include journey.html %}
</section>

<section class="section" aria-labelledby="writing-title">
  <p class="label"><b>04</b> / Writing &amp; Automation Lab</p>
  <div class="section-head"><h2 id="writing-title">Latest writing</h2><a href="{{ '/writing/' | relative_url }}">All posts →</a></div>
  {% if lab %}<p class="botline"><span class="dot" style="background:var(--live)" aria-hidden="true"></span>blog bot · <b>{{ lab.posts_published }}</b> posts published ·{% for p in lab.platforms %} {{ p[0] }} <b>{{ p[1] }}</b>{% unless forloop.last %} ·{% endunless %}{% endfor %} · <b>{{ lab.posts_queued }}</b> queued · updated {{ lab.updated | date: "%-d %b %Y" }}</p>{% endif %}
  <ul class="post-list post-cards">
    {% for post in site.posts limit: 3 %}<li data-series="{{ post.series }}"><a href="{{ post.url | relative_url }}"><span class="pd">{{ post.date | date: "%-d %b %Y" }}</span><span class="pt">{{ post.title }}</span></a></li>
    {% endfor %}
  </ul>
</section>

{% include cadentiq-cta.html variant="card" placement="home_card" %}
