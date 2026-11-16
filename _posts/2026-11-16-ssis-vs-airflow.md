---
id: 10
title: "Five Years of SSIS Pipelines: What I'd Build Differently Today (and What Airflow Got Right)"
slug: ssis-vs-airflow
description: "Comparing the GUI-first ETL world of SSIS with code-first orchestration, from someone who has run production pipelines in both mindsets."
series: data-engineering
tags: [dataengineering, airflow, etl, python]
image: "/images/malav-naik-tower-bridge-london.jpg"
image_alt: "Malav Naik on Tower Bridge with a red bus behind"
week: 5
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/ssis-vs-airflow/"
linkedin_intro: "I built SSIS pipelines over multi-million-record financial data for about five years. Looking at code-first orchestrators like Airflow, four things stand out that I'd do differently today: pipelines as code, explicit dependencies, safely re-runnable tasks and easy backfills. And a few things SSIS genuinely got right."
status: "ready"
---

![Malav Naik on Tower Bridge with a red bus behind – Five Years of SSIS Pipelines: What I'd Build Differently Today (and What Airflow Got Right)](/images/malav-naik-tower-bridge-london.jpg){: width="1200" height="1600"}

For about five years I built and maintained ETL pipelines in SQL Server Integration Services (SSIS) for multi-million-record financial datasets. SSIS did its job well. But looking at how modern data teams work, especially with code-first orchestrators like Apache Airflow, there's a lot I'd do differently.

Airflow started at Airbnb in 2014 to manage the company's growing web of data pipelines, was open-sourced the following year, and became an Apache project. Its design choices say a lot about what large data teams need.

## 1. Pipelines as code

SSIS packages are built visually and stored as XML. That's approachable, but code review is painful and diffs are almost unreadable.

Airflow defines pipelines (DAGs) in Python. That means pull requests, readable diffs, tests, and reuse through ordinary functions. **If I started again, I'd keep orchestration logic in plain code from day one**, whatever the tool.

## 2. Dependencies made explicit

In SSIS, dependencies between packages often lived in SQL Agent schedules: "job B runs at 3am because job A usually finishes by 2:30." That works until job A runs long.

A DAG states dependencies directly: B runs after A succeeds. No guessing from timetables.

## 3. Idempotent, re-runnable tasks

Airflow encourages tasks that can be re-run for a given date without side effects. Many SSIS packages I inherited assumed they ran exactly once, so a re-run meant manual clean-up. Designing every load to be safely repeatable is the single most valuable habit I've adopted. My [Dublin bikes pipeline](https://malavnaik.com/projects/dublin-bikes-pipeline/) is built this way: raw files are never overwritten, and the daily model rebuilds its last few hours, so a re-run gives exactly the same result. (I'll write a full post on idempotent pipelines later.)

## 4. Backfills as a first-class feature

Need to reload last March? In Airflow, you backfill a date range. In many SSIS setups, you edit parameters and hope. Treating time as a pipeline parameter makes history easy to rebuild.

## What SSIS got right

To be fair:

- **Performance on SQL Server is excellent.** Data flows inside the Microsoft stack are fast.
- **Low barrier for analysts.** Visual design let business-facing people maintain simple loads.
- **Tight integration** with SQL Server security and the rest of the Microsoft toolset.

## The lesson

The tool matters less than the principles: pipelines as code, explicit dependencies, idempotent tasks, easy backfills. You can apply all four in SSIS with discipline. Modern orchestrators just make them the default.
