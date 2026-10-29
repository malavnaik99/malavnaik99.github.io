---
title: "Employment Permits 2025 dashboard"
summary: "Which Irish sectors and employers sponsor work permits, and when – an interactive dashboard built from the official 2025 dataset."
problem: "International students in Ireland rarely know which employers sponsor work permits, or when hiring peaks."
approach: "Cleaned the official 2025 permits dataset, grouped companies into sectors and built a single-page Chart.js dashboard."
result: "A searchable, serverless dashboard of permits by sector, month and employer."
description: "An interactive dashboard by Data & GenAI Engineer Malav Naik analysing employment permits issued to companies in Ireland in 2025: sectors, top employers and monthly demand."
order: 8
featured: true
demo_url: /permits-2025/
code_url: https://github.com/malavnaik99/malavnaik99.github.io/tree/main/permits-2025
tech: [Excel, Data cleaning, Chart.js, JavaScript, Tailwind CSS]
---
## The problem
International students and early-career professionals in Ireland often don't know which employers actually sponsor work permits, or when in the year hiring peaks.

## What I built
A single-page dashboard over the official *Permits Issued to Companies – 2025* dataset: total permits, top sector, peak month and top employer, a monthly chart, a sector breakdown and a searchable table of top employers.

## How it works
1. Cleaned the public dataset: standardised company names and grouped companies into sectors.
2. Aggregated permits by company, sector and month.
3. Built the page with Chart.js and plain JavaScript, so it loads fast and needs no server.

## What I learned
Public labour-market data can answer very practical career questions, if it's cleaned and presented for the people asking them.
