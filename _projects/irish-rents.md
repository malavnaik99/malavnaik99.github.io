---
title: "Irish rents, 2008–2025: an open dataset, cleaned"
summary: "The official average rent of new tenancies in every Irish county, town and area since 2008, cleaned into one tidy, documented table and published on Kaggle and Hugging Face."
problem: "Ireland's official rent table has 674,352 rows, codes repeated as labels and 70% empty cells."
approach: "A reproducible Python cleaning pipeline with a Kaggle notebook that rebuilds the data from the official source."
result: "201,912 rents for 437 places, 2008–2025, published on Kaggle and Hugging Face."
description: "Malav Naik's cleaned open dataset of RTB average rents from the CSO, 2008–2025, with a reproducible cleaning notebook, on Kaggle and Hugging Face."
order: 5
featured: true
code_url: https://github.com/malavnaik99/irish-rents-dataset
demo_url: https://www.kaggle.com/datasets/malavnaik/irish-rents-rtb
tech: [Python, pandas, Kaggle, Hugging Face Datasets, GitHub Actions, CSO open data]
---
## The problem
Ireland publishes excellent open data on rents. The Residential Tenancies Board (RTB) records the average rent of every new tenancy, and the Central Statistics Office (CSO) publishes it. But the raw table is hard to use: 674,352 rows, every category repeated as a code and a label, and **70% of the cells empty**.

## What I built
A reproducible cleaning pipeline that turns the official table into **one tidy, documented dataset**:

- **201,912 rents**, every half-year from **2008 to 2025**
- **437 places**: all 26 counties, 36 towns, cities and Dublin postal districts, and 375 smaller areas
- by number of bedrooms and property type

It's published on [Kaggle](https://www.kaggle.com/datasets/malavnaik/irish-rents-rtb) and [Hugging Face](https://huggingface.co/datasets/Malavnaik/irish-rents-rtb), with a [Kaggle notebook](https://www.kaggle.com/code/malavnaik/cleaning-irish-rents-rtb) that shows every cleaning step and rebuilds the data from the official source.

## How it was cleaned
1. **Readable columns:** keep the labels, drop the repeated codes and the columns that never change.
2. **Empty means "not published", not zero.** The RTB leaves a cell empty when too few new tenancies were registered for a reliable average. Those rows are dropped and the reason is documented, so nobody averages in a zero.
3. **Label every place** as a county, a town or district, or a smaller area. My first attempt guessed the level from the CSO's location codes and found only 4 "counties", so I switched to matching the 26 county names.
4. **Flag the totals.** "All bedrooms", "1 to 2 bed" and "All property types" are sums of other rows, so they're marked to stop anyone adding them up twice.
5. **Check before publishing:** one row per half-year, place, bedrooms and property type, and every rent between €50 and €20,000.

A GitHub Actions workflow runs the cleaning, publishes the files with a data card, and runs the same notebook on Kaggle. Both runs produce the same 201,912 rows.

## What the data shows
Average monthly rent for a new tenancy, all homes:

<svg viewBox="0 0 640 330" role="img" aria-labelledby="rent-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="16">
  <title id="rent-title">Line chart of average monthly rent for new tenancies, 2008 to 2025: Dublin falls from €1,325 to €1,004 in 2011, then rises to €2,162; Cork goes from €921 to a low of €710 and up to €1,558; Leitrim from €551 to a low of €398 and up to €1,010.</title>
  <g fill="none" stroke="currentColor" stroke-opacity="0.25" stroke-width="1">
    <path d="M70 290H510"/>
    <path d="M70 234H510"/>
    <path d="M70 178H510"/>
    <path d="M70 121H510"/>
    <path d="M70 65H510"/>
  </g>
  <g fill="currentColor" text-anchor="end">
    <text x="62" y="295">€0</text>
    <text x="62" y="239">€500</text>
    <text x="62" y="182">€1,000</text>
    <text x="62" y="126">€1,500</text>
    <text x="62" y="70">€2,000</text>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="70" y="318">2008</text>
    <text x="171" y="318">2012</text>
    <text x="271" y="318">2016</text>
    <text x="372" y="318">2020</text>
    <text x="472" y="318">2024</text>
  </g>
  <polyline points="70.0,140.9 82.6,147.0 95.1,154.7 107.7,163.3 120.3,171.3 132.9,174.9 145.4,177.1 158.0,176.0 170.6,175.8 183.1,173.8 195.7,172.9 208.3,168.2 220.9,164.3 233.4,156.7 246.0,151.6 258.6,144.5 271.1,141.3 283.7,133.8 296.3,128.1 308.9,120.5 321.4,113.7 334.0,107.0 346.6,102.6 359.1,98.4 371.7,96.7 384.3,94.9 396.9,94.2 409.4,90.7 422.0,85.6 434.6,79.8 447.1,73.7 459.7,68.6 472.3,61.6 484.9,56.7 497.4,50.8 510.0,46.8" fill="none" stroke="currentColor" stroke-width="3"/>
  <text x="518" y="52" fill="currentColor">Dublin €2,162</text>
  <polyline points="70.0,186.4 82.6,188.8 95.1,194.0 107.7,198.7 120.3,203.7 132.9,205.7 145.4,208.6 158.0,208.4 170.6,210.1 183.1,208.4 195.7,209.1 208.3,207.0 220.9,207.2 233.4,201.9 246.0,202.2 258.6,197.1 271.1,194.6 283.7,188.5 296.3,184.9 308.9,179.8 321.4,177.3 334.0,173.2 346.6,171.4 359.1,167.5 371.7,166.8 384.3,163.4 396.9,162.5 409.4,158.6 422.0,156.0 434.6,150.6 447.1,148.8 459.7,141.8 472.3,137.8 484.9,129.5 497.4,123.6 510.0,114.7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-dasharray="8 5"/>
  <text x="518" y="120" fill="currentColor">Cork €1,558</text>
  <polyline points="70.0,228.0 82.6,229.2 95.1,232.5 107.7,235.4 120.3,238.7 132.9,240.5 145.4,242.5 158.0,243.4 170.6,244.6 183.1,245.0 195.7,245.2 208.3,245.0 220.9,244.0 233.4,243.4 246.0,242.0 258.6,240.6 271.1,238.9 283.7,237.3 296.3,235.6 308.9,234.2 321.4,231.4 334.0,230.3 346.6,228.2 359.1,227.0 371.7,225.3 384.3,224.5 396.9,222.6 409.4,220.2 422.0,213.6 434.6,208.4 447.1,204.8 459.7,201.3 472.3,194.4 484.9,186.8 497.4,180.0 510.0,176.4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-dasharray="2 4"/>
  <text x="518" y="181" fill="currentColor">Leitrim €1,010</text>
</svg>


- **Dublin** fell from €1,325 in early 2008 to **€1,004 in early 2011**, then more than doubled to **€2,162** by late 2025.
- In the last ten years (late 2015 to late 2025), rents **at least doubled in 17 of the 26 counties**. The biggest rises were in **Longford (+156%)**, **Limerick (+146%)** and **Roscommon (+133%)**. Dublin rose 67%, from a much higher starting point.
- Late 2025, the most expensive counties were **Dublin (€2,162)**, **Wicklow (€1,739)** and **Kildare (€1,719)**; the least expensive were **Donegal (€992)**, **Leitrim (€1,010)** and **Monaghan (€1,034)**.

*These are averages for **new** tenancies only, not what all tenants pay, and they're not adjusted for inflation.*

## Data and credits
Source: CSO table [RIH02](https://data.cso.ie/table/RIH02), "RTB Average Monthly Rent Report", © Central Statistics Office and Residential Tenancies Board, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The cleaned dataset uses the same licence.

## Links
- [Dataset on Kaggle](https://www.kaggle.com/datasets/malavnaik/irish-rents-rtb)
- [Cleaning notebook on Kaggle](https://www.kaggle.com/code/malavnaik/cleaning-irish-rents-rtb)
- [Dataset on Hugging Face](https://huggingface.co/datasets/Malavnaik/irish-rents-rtb)
- [Code on GitHub](https://github.com/malavnaik99/irish-rents-dataset)
