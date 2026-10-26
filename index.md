---
layout: default
wide: true
---
{% assign lab = site.data.automation %}

<section class="hero" aria-labelledby="hero-title">
  <div>
    <p class="label">Data &amp; GenAI Engineer · ~10 years · Dublin</p>
    <h1 id="hero-title">I build data pipelines and GenAI systems, and prove they work.</h1>
    <p class="sub">About 10 years in data, from SSIS pipelines and an Azure SQL migration at S&amp;P Global Market Intelligence to dbt, DuckDB and LLM tools today. Every project here shows its code and measured results.</p>

    <div class="ask card" role="region" aria-labelledby="ask-title">
      <p class="label" id="ask-title">Ask about my work</p>
      <form id="ask-form">
        <label class="sr-only" for="ask-input">Your question</label>
        <input id="ask-input" type="text" placeholder="e.g. How do you test a data pipeline?" autocomplete="off">
        <button class="btn btn-accent" type="submit">Ask</button>
      </form>
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
      <div class="answer" id="ask-soon" hidden>
        <p>Coming soon: free-text answers are still being built. Try one of the example questions for now.</p>
      </div>
    </div>
  </div>

  <figure class="card card-big photo-card" style="margin:0">
    <img src="{{ '/images/malav-naik-portrait.jpg' | relative_url }}" alt="Malav Naik in a navy suit outside the Convention Centre Dublin" width="480" height="480" fetchpriority="high">
    <dl class="readout">
      <dt>name</dt><dd>Malav Naik</dd>
      <dt>based</dt><dd>Dublin, Ireland</dd>
      <dt>focus</dt><dd>data pipelines · GenAI · AI automation</dd>
      <dt>pipeline</dt><dd data-pipeline><span class="dot" aria-hidden="true"></span><span class="status">runs every 15 min</span></dd>
    </dl>
  </figure>
</section>

<ul class="metrics" aria-label="Key numbers">
  <li><span class="num">~10 yrs</span><span class="what">in data, across India and Ireland</span></li>
  <li><span class="num">0.957</span><span class="what">ROC-AUC, content moderation model</span></li>
  <li><span class="num">15 min</span><span class="what">pipeline refresh, €0 a month</span></li>
  <li><span class="num">MSc</span><span class="what">Data Analytics, National College of Ireland</span></li>
</ul>

<section class="section" aria-labelledby="featured-title">
  <p class="label"><b>01</b> / Featured project</p>
  <article class="card card-big">
    <div class="featured-top">
      <h2 id="featured-title"><a href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}" style="color:inherit;text-decoration:none">Dublin bikes + weather data pipeline</a></h2>
      <span class="badge" data-pipeline><span class="dot" aria-hidden="true"></span><span class="status">running every 15 minutes</span></span>
    </div>
    <p class="muted" style="max-width:46rem">Collects every Dublinbikes station every 15 minutes, models it with dbt and DuckDB into a tested star schema, and feeds a live dashboard, on free tiers only.</p>
    <ul class="stats">
      <li><span class="num">15 min</span><span class="what">collection interval</span></li>
      <li><span class="num">14</span><span class="what">automatic data tests on every run</span></li>
      <li><span class="num">€0</span><span class="what">monthly cost</span></li>
    </ul>
    <ol class="flow" aria-label="How the pipeline works">
      <li><b>Source</b><span>Dublinbikes + Met Éireann</span></li>
      <li><b>DuckDB staging</b><span>types, time zones, de-duplication</span></li>
      <li><b>dbt marts</b><span>star schema · 14 tests</span></li>
      <li><b>Parquet on Hugging Face</b><span>public dataset</span></li>
      <li><b>Dashboard + SQL console</b><span>in your browser</span></li>
    </ol>
    <p class="actions">
      <a class="btn btn-accent" href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}#sql">Run SQL in your browser</a>
      <a class="btn" href="{{ '/projects/dublin-bikes-pipeline/' | relative_url }}">Case study</a>
    </p>
  </article>
</section>

<section class="section" aria-labelledby="more-title">
  <p class="label"><b>02</b> / More projects</p>
  <h2 id="more-title" class="sr-only">More projects</h2>
  <div class="rows">
    <details class="row">
      <summary><span class="n">01</span><span class="t">Content moderation classifier, with a fairness check</span><span class="m">ROC-AUC 0.957</span><span class="pm" aria-hidden="true"></span></summary>
      <div class="row-body"><div>
        <p>A toxicity classifier trained on 1.8 million public comments, with review-queue thresholds, a prevalence estimate and a fairness check by identity group, plus a demo that runs in your browser.</p>
        <ul class="chips" aria-label="Stack"><li>Python</li><li>scikit-learn</li><li>PyTorch</li><li>DistilBERT</li><li>ONNX</li><li>transformers.js</li></ul>
        <div class="sandbox"><p class="label">Sandbox</p><p class="small muted">The interactive threshold sandbox is coming next. For now, <a href="{{ '/projects/moderation-classifier/' | relative_url }}">read the case study</a>.</p></div>
      </div></div>
    </details>
    <details class="row">
      <summary><span class="n">02</span><span class="t">Ask the EU Digital Services Act</span><span class="m">84% top-3 hit rate</span><span class="pm" aria-hidden="true"></span></summary>
      <div class="row-body"><div>
        <p>Type a question in plain English and get the articles of the EU Digital Services Act that answer it, quoted and linked. Tested on 25 questions: semantic search put the right article in the top 3 for 84% of them.</p>
        <ul class="chips" aria-label="Stack"><li>Python</li><li>BM25</li><li>sentence-transformers</li><li>transformers.js</li><li>Hugging Face</li></ul>
        <div class="sandbox"><p class="label">Sandbox</p><p class="small muted">A BM25 vs vector comparison is coming next. For now, <a href="{{ '/projects/ask-the-dsa/' | relative_url }}">read the case study</a>.</p></div>
      </div></div>
    </details>
    <details class="row">
      <summary><span class="n">03</span><span class="t">SkillBot: from job title to the skills it needs</span><span class="m">48% skill match</span><span class="pm" aria-hidden="true"></span></summary>
      <div class="row-body"><div>
        <p>My MSc project on personalised learning with LLMs and knowledge graphs, plus a free, tested rebuild: type a job title and see the skills real job ads ask for. In a leave-one-out test on 1,167 ads, 48% of suggested skills were in the real ad.</p>
        <ul class="chips" aria-label="Stack"><li>Python</li><li>Knowledge graphs</li><li>sentence-transformers</li><li>transformers.js</li></ul>
        <div class="sandbox"><p class="label">Sandbox</p><p class="small"><a class="btn small" href="https://huggingface.co/spaces/Malavnaik/skillbot-skills-explorer">Open the skills explorer</a> <a href="{{ '/projects/skillbot/' | relative_url }}">Case study</a></p></div>
      </div></div>
    </details>
    <details class="row">
      <summary><span class="n">04</span><span class="t">Automation Lab: blog publishing with Telegram approval</span><span class="m">{{ lab.posts_published }} posts published</span><span class="pm" aria-hidden="true"></span></summary>
      <div class="row-body"><div>
        <p>A bot that writes nothing until I approve on Telegram, then publishes each post to this site, DEV and LinkedIn, running for free on GitHub Actions.</p>
        <ul class="chips" aria-label="Stack"><li>Python</li><li>GitHub Actions</li><li>Telegram Bot API</li><li>DEV API</li><li>LinkedIn API</li></ul>
        <div class="sandbox"><p class="label">Sandbox</p><p class="small muted">An animated walk-through of the approval flow is coming next. For now, <a href="{{ '/projects/blog-automation-bot/' | relative_url }}">read the case study</a>.</p></div>
      </div></div>
    </details>
  </div>
  <p style="margin-top:1.25rem"><a href="{{ '/work/' | relative_url }}">All projects →</a></p>
</section>

<section class="section" id="toolkit" aria-labelledby="toolkit-title">
  <p class="label"><b>03</b> / Toolkit</p>
  <h2 id="toolkit-title">Tools I've used in real projects</h2>
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
</section>

{% include product-card.html %}

<section class="section" id="journey" aria-labelledby="journey-title">
  <p class="label"><b>04</b> / From Surat to Dublin</p>
  <h2 id="journey-title">Ten years, two countries, one thread: data</h2>
  {% include journey.html %}
</section>

<section class="section" aria-labelledby="writing-title">
  <p class="label"><b>05</b> / Writing &amp; Automation Lab</p>
  <div class="section-head"><h2 id="writing-title">Latest writing</h2><a href="{{ '/writing/' | relative_url }}">All posts →</a></div>
  {% if lab %}<p class="botline"><span class="dot" style="background:var(--live)" aria-hidden="true"></span>blog bot · <b>{{ lab.posts_published }}</b> posts published ·{% for p in lab.platforms %} {{ p[0] }} <b>{{ p[1] }}</b>{% unless forloop.last %} ·{% endunless %}{% endfor %} · <b>{{ lab.posts_queued }}</b> queued · updated {{ lab.updated | date: "%-d %b %Y" }}</p>{% endif %}
  <ul class="post-list">
    {% for post in site.posts limit: 3 %}<li><a href="{{ post.url | relative_url }}"><span class="pd">{{ post.date | date: "%-d %b %Y" }}</span><span class="pt">{{ post.title }}</span></a></li>
    {% endfor %}
  </ul>
</section>

