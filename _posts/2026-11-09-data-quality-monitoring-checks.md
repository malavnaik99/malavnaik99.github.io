---
id: 7
title: "The Data Quality Checks That Catch Problems Before Your Users Do"
slug: data-quality-monitoring-checks
description: "Six simple, automatable checks that stop bad data reaching dashboards, with SQL you can adapt."
series: data-engineering
tags: [dataquality, sql, dataengineering, analytics]
image: "/images/malav-naik-google-ireland-world-map-wall.jpg"
image_alt: "Malav Naik in front of the Google Ireland moss world map wall"
week: 4
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/data-quality-monitoring-checks/"
linkedin_intro: "The worst way to find a data problem is a message asking why the dashboard says revenue dropped 90% overnight. After years of pipelines on multi-million-record financial data, these are the six simple checks I'd put on any load: freshness, volume, completeness, uniqueness, referential integrity and business rules, with SQL you can adapt today."
status: "ready"
---

![Malav Naik in front of the Google Ireland moss world map wall – The Data Quality Checks That Catch Problems Before Your Users Do](/images/malav-naik-google-ireland-world-map-wall.jpg){: width="1512" height="1512"}

The worst way to find a data problem is a message from an executive asking why the dashboard says revenue dropped 90% overnight. Over years of building pipelines on multi-million-record financial datasets, I learned that a handful of simple checks prevent most of those messages.

None of these need a special tool. They're SQL queries that run after each load and fail loudly.

## 1. Freshness: did the data arrive?

```sql
SELECT MAX(loaded_at) AS last_load
FROM sales.fact_orders
HAVING MAX(loaded_at) < DATEADD(hour, -26, SYSUTCDATETIME());
```

If this returns a row, the daily load is late. Alert before anyone opens a report.

## 2. Volume: did roughly the right amount arrive?

Compare today's row count with a trailing average. A drop or spike of more than, say, 30% usually means an upstream change.

```sql
WITH daily AS (
  SELECT CAST(order_date AS date) AS d, COUNT(*) AS n
  FROM sales.fact_orders
  WHERE order_date >= DATEADD(day, -15, CAST(SYSUTCDATETIME() AS date))
  GROUP BY CAST(order_date AS date)
)
SELECT d, n, AVG(n) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg_prev
FROM daily;
```

## 3. Completeness: are key columns null?

```sql
SELECT COUNT(*) AS missing_customer
FROM sales.fact_orders
WHERE customer_id IS NULL AND loaded_at >= @batch_start;
```

## 4. Uniqueness: are there duplicates?

Duplicate keys silently double-count everything downstream.

```sql
SELECT order_id, COUNT(*)
FROM sales.fact_orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

## 5. Referential integrity: do the joins still work?

```sql
SELECT COUNT(*) AS orphan_rows
FROM sales.fact_orders f
LEFT JOIN sales.dim_customer c ON c.customer_id = f.customer_id
WHERE c.customer_id IS NULL;
```

## 6. Business rules: does the data make sense?

Negative quantities, end dates before start dates, prices outside a plausible range. Write the rules down with the business owner, then encode them.

## Making it stick

- **Run checks in the pipeline, not after.** A failed check should stop the load or flag the batch.
- **Log results to a table.** Trends in check failures tell you which sources are unreliable.
- **Alert the right person.** A failure nobody sees is the same as no check.

## A real example

My [Dublin bikes data pipeline](https://malavnaik.com/projects/dublin-bikes-pipeline/) runs these checks every morning as dbt tests: freshness (the newest data must be under two hours old), volume (at least 72 collector runs in the last 24 hours), uniqueness (one row per station per hour), and joins to the station and hour tables. If any fails, I get a Telegram message before anyone looks at the dashboard.

Tools like dbt tests and Great Expectations package these ideas nicely. But the ideas matter more than the tool, and you can start today with plain SQL.
