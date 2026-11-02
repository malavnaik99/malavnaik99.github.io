---
id: 53
title: "70% of Ireland's Rent Table Is Empty. Here's How I Cleaned It"
slug: cleaning-irish-rents-open-data
description: "How I turned the official Irish rent table (RTB, via the CSO) into one tidy, documented open dataset, and what 18 years of rents show."
series: data-engineering
tags: [opendata, python, datacleaning, ireland]
image: "/images/malav-naik-cliffs-of-moher.jpg"
image_alt: "Malav Naik standing at the Cliffs of Moher"
week: 27
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/cleaning-irish-rents-open-data/"
linkedin_intro: "Ireland publishes the average rent of every new tenancy since 2008, but 70% of the official table is empty cells, and every category appears twice. I cleaned it into one tidy, documented dataset (201,912 rents, 437 places) and published it on Kaggle and Hugging Face. Here's what the cleaning involved, and what 18 years of rents show."
x_post: "70% of Ireland's official rent table is empty cells. I cleaned it into one open dataset: 201,912 rents, 437 places, 2008–2025. Average Dublin rent for a new tenancy: €1,004 in 2011, €2,162 in 2025."
reddit: {"community": "r/ireland", "title": "I cleaned the official RTB rent figures (2008–2025) into one free dataset: average rents for new tenancies at least doubled in 17 of 26 counties in 10 years", "text": "Source: the CSO/RTB table of average rents for new tenancies. 70% of its cells are blank because too few tenancies were registered, so I documented that rather than filling gaps. Not adjusted for inflation. Free to use under CC BY 4.0, happy to answer questions about the data."}
status: ready
---

![Malav Naik standing at the Cliffs of Moher – 70% of Ireland's Rent Table Is Empty. Here's How I Cleaned It](/images/malav-naik-cliffs-of-moher.jpg){: width="1440" height="1440"}

Ireland has some of the best open rent data in Europe. The Residential Tenancies Board (RTB) records the rent of every new tenancy, and the Central Statistics Office (CSO) publishes the averages, every half-year since 2008, for counties, towns and small areas.

I wanted to use it for a quick analysis and found the raw table hard to work with. So I cleaned it properly and published the result as an open dataset on [Kaggle](https://www.kaggle.com/datasets/malavnaik/irish-rents-rtb) and [Hugging Face](https://huggingface.co/datasets/Malavnaik/irish-rents-rtb).

## What's wrong with the raw table

The CSO table (RIH02) has 674,352 rows. Three things make it awkward:

- **Every category appears twice**, once as a code and once as a label, plus columns that never change.
- **Places of very different sizes are mixed together**: counties, towns, Dublin postal districts and small areas sit in one column with nothing saying which is which.
- **70% of the rent cells are empty.**

## Empty doesn't mean zero

The empty cells are the most important part. The RTB leaves a cell empty when too few new tenancies were registered to give a reliable average. It's mostly small areas and specific bedroom counts: 86% of "one bed" cells are empty, against 50% for "all bedrooms".

If you load the file and fill those gaps with zeros, or let a tool do it quietly, every average you compute is wrong. So I dropped them and wrote down why in the data card. 201,912 published rents remain.

## Labelling places: my first try was wrong

I first guessed each place's level from the CSO's location codes, assuming counties ended in four zeros. The check I printed found only **4 "counties"**, and one of them was Christchurch, an area of Dublin city. So the guess was wrong, and the printout caught it before anything was published.

I switched to matching the 26 county names. Everything without a comma ("Carlow Town", "Dublin 8") is a town or district, and everything with one ("Tullow, Carlow") is a smaller area: 26 counties, 36 towns and districts, 375 areas.

## Totals, flagged

"All bedrooms", "1 to 2 bed" and "All property types" are sums of other rows. Leaving them unmarked invites double counting, so each row has two true/false columns that say whether it's a total.

## Checks, then publish

Before anything goes out, the pipeline asserts one row per half-year, place, bedrooms and property type, and that every rent is between €50 and €20,000. A GitHub Actions workflow downloads the official table, cleans it, publishes the files with a data card, and runs the same code as a [Kaggle notebook](https://www.kaggle.com/code/malavnaik/cleaning-irish-rents-rtb). Both produce the same 201,912 rows. The [code is on GitHub](https://github.com/malavnaik99/irish-rents-dataset).

## What 18 years of rents show

Average monthly rent for a new tenancy, all homes:

- **Dublin** fell from €1,325 in early 2008 to **€1,004 in early 2011**, then more than doubled to **€2,162** by late 2025.
- Over the last ten years, rents **at least doubled in 17 of 26 counties**. The biggest rises were in **Longford (+156%)**, **Limerick (+146%)** and **Roscommon (+133%)**. Dublin rose 67%, from a much higher base.
- Late 2025, the most expensive counties were Dublin (€2,162), Wicklow (€1,739) and Kildare (€1,719). The least expensive were Donegal (€992), Leitrim (€1,010) and Monaghan (€1,034).

These are averages for **new** tenancies, not what all tenants pay, and they aren't adjusted for inflation. The chart is on the [project page](https://malavnaik.com/projects/irish-rents/).

## What I'd do next

- **Adjust for inflation** using the CSO's consumer price index, so 2008 and 2025 rents can be compared fairly.
- **Add tenancy counts**, if the RTB publishes them, so users can see how reliable each average is.

The dataset is free to use under CC BY 4.0. If you build something with it, I'd love to see it.
