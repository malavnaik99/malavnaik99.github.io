---
id: 3
title: "Migrating On-Prem SQL Server to Azure SQL PaaS: How We Cut Infrastructure Costs by 25%"
slug: azure-sql-migration-25-percent
description: "Lessons from moving production SQL Server databases to Azure SQL PaaS without disrupting the people who depend on them."
series: data-engineering
tags: [azure, sql, dataengineering, cloud]
image: "/images/malav-naik-london-skyline.jpg"
image_alt: "Malav Naik on a rooftop with a city skyline behind"
week: 2
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik99.github.io/blog/azure-sql-migration-25-percent/"
status: ready
linkedin_intro: "At S&P Global I helped move 10 to 50 SQL Server databases to Azure SQL Managed Instance, cutting infrastructure costs by about 25%. The savings came from right-sizing, but the real problems were hard-coded connections, SSIS jobs and local file paths. Here are six lessons from that migration."
---

![Malav Naik on a rooftop with a city skyline behind – Migrating On-Prem SQL Server to Azure SQL PaaS: How We Cut Infrastructure Costs by 25%](/images/malav-naik-london-skyline.jpg)

At S&P Global Market Intelligence I helped migrate on-premise SQL Server databases to Azure SQL PaaS. Our team moved between 10 and 50 databases to Azure SQL Managed Instance. The headline result was a reduction in infrastructure costs of about 25%. The more important result was that the people using those databases barely noticed it happened.

Here's what I learned about doing a migration like that well.

## 1. Inventory before you plan

Before choosing a target, list everything that touches the database: ETL jobs, reports, linked servers, SQL Agent jobs, cross-database queries, CLR assemblies. PaaS options don't support every on-prem feature in the same way, and you want to find the gaps on a spreadsheet, not in production.

Microsoft's Data Migration Assistant and Azure Migrate help here, but they don't know about the Excel workbook someone in finance refreshes every Monday. Talk to users.

## 2. Pick the right PaaS flavour

Azure SQL Database and Azure SQL Managed Instance trade compatibility against simplicity. Managed Instance keeps more instance-level features (Agent jobs, cross-database queries), so it suits lift-and-shift. Single databases are simpler and can be cheaper, but may need refactoring. Decide per workload, not per estate. We went with Managed Instance, which kept most instance-level features in place and meant fewer changes to existing code.

## 3. Right-size, don't copy

Most of the savings came from not paying for capacity we didn't use. On-prem servers are sized for peak load plus growth plus fear. In the cloud you can measure actual usage and scale. Look at real CPU, memory and IO over several weeks before choosing service tiers.

## 4. Migrate in waves

Start with low-risk databases: development, reporting copies, internal tools. Each wave teaches you something about networking, permissions or performance that makes the next wave smoother.

## 5. Test the boring things

Performance gets attention. In our migration, the real problems came from elsewhere:

- Connection strings hard-coded in old applications and reports
- SSIS packages and SQL Agent jobs that needed reworking to run against Azure
- Jobs that relied on local file paths on the old servers

Also worth checking: time zone and collation differences, firewall rules and private endpoints.

## 6. Define "done" with the users

A migration isn't finished when the data moves. It's finished when every report, job and application works as before and the old servers are switched off. Agree that checklist with stakeholders up front.

## The takeaway

Cloud migration savings come mostly from right-sizing and retiring infrastructure. Keeping users happy comes from inventory, testing and communication. Neither is glamorous, and both matter more than the migration tooling.
