---
id: 14
title: "Designing Analytics-Ready Data Models: Star Schema Lessons from Financial Data"
slug: analytics-ready-data-models
description: "Practical dimensional modelling advice for analysts and engineers who want dashboards that are fast, correct and easy to extend."
series: data-engineering
tags: [datamodeling, sql, powerbi, dataengineering]
image: "/images/malav-naik-dublin-docklands-waterfront.jpg"
image_alt: "Malav Naik leaning against a red pole by the water"
week: 7
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/analytics-ready-data-models/"
status: "ready"
linkedin_intro: "Most \"slow dashboard\" and \"wrong number\" problems are modelling problems in disguise. Working with multi-million-record financial data taught me the practical version of dimensional modelling: start from the questions the business asks, declare the grain, keep facts narrow and dimensions wide, use surrogate keys, decide how to handle history, and build a proper date table."
---

![Malav Naik leaning against a red pole by the water – Designing Analytics-Ready Data Models: Star Schema Lessons from Financial Data](/images/malav-naik-dublin-docklands-waterfront.jpg){: width="1200" height="1599"}

A dashboard is only as good as the model underneath it. Working with multi-million-record financial datasets taught me that most "slow dashboard" and "wrong number" problems are modelling problems in disguise.

Here's the practical version of dimensional modelling I wish I'd had on day one.

## Start with the questions, not the tables

Before designing anything, write down the 10 questions the business asks most. "Revenue by region by month." "Top clients by product." Each question names a measure (revenue) and the ways people slice it (region, month, product). Measures become **facts**. Slicers become **dimensions**.

## Declare the grain first

The grain is what one row in a fact table represents: one order line, one daily balance, one trade. Write it down in a sentence. Most double-counting bugs come from mixing grains, for example joining daily balances to individual transactions.

## Keep facts narrow and dimensions wide

- **Fact tables**: keys plus numeric measures. Many rows, few columns.
- **Dimension tables**: descriptive attributes. Fewer rows, many columns.

This is the star schema. It's popular because it's easy to understand and tools like Power BI are optimised for it.

## Use surrogate keys

Source system IDs change, collide between systems, and sometimes get reused. A surrogate key (a simple integer generated in the warehouse) insulates your model from those problems.

## Handle history deliberately

When a client moves from one region to another, should old revenue stay with the old region or move to the new one? That's a business decision, not a technical one.

- **Type 1**: overwrite. History moves with the change.
- **Type 2**: add a new row with valid-from and valid-to dates. History stays where it was.

Ask the business which they want, per attribute.

## Build a proper date dimension

A date table with fiscal periods, holidays and week numbers saves endless calculation in reports. Every BI tool works better with one.

## Test the model with the original questions

Once built, answer each of your 10 questions with a simple query. If any needs a complicated workaround, the model isn't finished.

Good modelling is the closest thing data work has to compound interest. Every report built on a clean model is faster to build, and easier to trust.
