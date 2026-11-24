---
layout: default
title: "Ireland Guides: Rent, Dublin Bikes and Living in Ireland"
seo_title: "Ireland Guides: Rent, Dublin Bikes & More"
breadcrumb: "Ireland Guides"
permalink: /ireland-guides/
description: "Free guides to living in Ireland by Malav Naik: average rents in every county from official RTB data and Dublin Bikes statistics from open data."
# A guide is listed only once its page exists, so nothing here links to a page that isn't built yet.
guides:
  - url: /rent/
    name: "Irish Rent Reality Check"
    text: "The average new rent in every county, town and Dublin district since 2008, how much of a typical wage it takes, and a page for each of the 26 counties. Official RTB data via the CSO, refreshed weekly."
  - url: /dublin-bikes/
    name: "Dublin Bikes statistics"
    text: "Estimated pickups per month, the busiest and quietest stations, the busiest hours and how rain changes use. Updated monthly from open Dublinbikes and Met Éireann data."
  - url: /living-in-ireland/
    name: "Living in Ireland: stamp by stamp"
    text: "For each immigration stamp, the official pages to check for work, healthcare, tax, payments, housing and citizenship."
---
<p class="label">Ireland Guides</p>
<h1>Ireland Guides</h1>
<p class="lead">Free, practical guides for anyone living in Ireland or planning a move here, built from official and open data. Each one shows where its numbers come from and when they were last updated.</p>

{% for g in page.guides %}{% assign live = site.html_pages | where: "url", g.url | first %}{% if live %}
## [{{ g.name }}]({{ g.url | relative_url }})
{{ g.text }}
{% endif %}{% endfor %}

I'm Malav Naik, a Data & GenAI Engineer in Dublin. I build these as open-data projects: [read how they're made]({{ '/work/' | relative_url }}), or [tell me about an error]({{ '/contact/' | relative_url }}).
