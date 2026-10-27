---
# One-off manual post (27 Oct 2026). It lives only here, not in the blog bot's blog/posts/, so the bot never queues,
# counts or cross-posts it. Malav shares it on LinkedIn, DEV and Medium himself.
title: "Why '2 Hours of Maintenance' Becomes 3 Days: The Engineering Behind Failed Deployments and Rollbacks"
slug: maintenance-window-failed-deployment-rollback
description: "What turns a short maintenance window into days? A visual guide to failed deployments, database migrations and rollback, with Employment Permits Online as a case study."
series: data-engineering
tags: [devops, deployment, rollback, incident-response, site-reliability, database-migration, data-engineering, cloud]
image: { path: /images/og-maintenance-window-rollback.png, width: 1200, height: 627, alt: "Rollback decision tree: did the schema change, is it backward compatible, can we fix forward, or restore from backup" }
canonical_url: "https://malavnaik.com/blog/maintenance-window-failed-deployment-rollback/"
minutes: 8  # reading time for the main text; the collapsed deep dives are optional
tldr: "Maintenance windows are planned around everything going right. They stretch into days when a step fails at production scale and the change can't simply be undone: rolling back code takes minutes, but rolling back data means restores, lost writes and reconciliation. Expand/contract migrations, blue-green deploys and rehearsed restores keep failures small."
faq:
  - q: "Why is rolling back a database harder than rolling back code?"
    a: "Code has no memory: you redeploy the old version and it behaves as before. A database keeps everything written since the change. Undoing it usually means restoring a backup, which loses the writes made after it, so someone has to reconcile them."
  - q: "What are RPO and RTO?"
    a: "RPO (recovery point objective) is how much data you can afford to lose, measured as time since the last good backup. RTO (recovery time objective) is how long you can afford to be down while you restore."
  - q: "Why can one schema change freeze a whole website?"
    a: "Most ALTER TABLE statements need an exclusive lock. If a long query is reading the table, the ALTER waits, and every new query queues behind it. Setting lock_timeout makes the ALTER give up after a few seconds so it can retry later."
  - q: "What is an expand/contract migration?"
    a: "A way to change a database schema in small, reversible steps across several releases: add the new structure, move the application and data over while both work, and only remove the old structure once nothing uses it."
last_modified_at: 2026-10-27
---

As I write this on 27 October 2026, Ireland's **Employment Permits Online** portal has shown this page for about three days:

> "Site Unavailable. This site is unavailable due to essential maintenance. We apologise for any inconvenience caused and hope to resume normal service as soon as possible."

An earlier notice on the portal announced a three-hour **maintenance window** (Tuesday 6 October, 6pm to 9pm). That's what planned maintenance usually looks like. So what can turn hours into days? We don't know the reason in this case, so this post doesn't guess. Instead it walks through one common *what if*: a **failed deployment** that can't be cleanly **rolled back**, especially when a **database migration** is involved.

<aside class="tldr" markdown="1">
<p class="eyebrow">About this case study</p>
This post uses the Employment Permits Online maintenance as the starting point for a general engineering study. The portal is run by the Department of Enterprise, Tourism and Employment (DETE), and the reason for the extended maintenance hasn't been shared publicly, so nothing here describes what happened on the portal. The failed-deployment scenario is a what-if, chosen because it's one of the most common ways any maintenance window grows. Keeping a national service safe during maintenance is careful work, and taking extra time is often the right call.
</aside>

**The portal in brief:** a cloud-based system for Irish work permit applications, live since 28 April 2025, when it replaced the older EPOS system. It uses email verification and multi-factor authentication (MFA), and appears to be hosted on Microsoft Azure App Service.

## A normal maintenance window

A well-run window follows a script. About two hours of work, plus an hour of buffer for small surprises.

<figure class="fig" id="figure-1">
{% include diagrams/maintenance-window-wide.svg %}
{% include diagrams/maintenance-window-narrow.svg %}
<figcaption>Figure 1 — A normal maintenance window: announce, freeze, holding page, backup, deploy, migrate, test, reopen.</figcaption>
</figure>

<details class="deep" markdown="1">
<summary>Deep dive: what each step is for</summary>

- **Announce, freeze:** users plan around the date; no other changes go in, so if something breaks there's one suspect.
- **Holding page:** the load balancer or gateway (the front door all requests pass through) shows a static page, so no new data arrives mid-change.
- **Backup and snapshot:** taken *after* traffic stops, so it's complete and consistent.
- **Deploy, then migrations:** a *schema migration* changes the database's structure (add a column); a *data migration* changes its contents (convert every phone number).
- **Smoke tests:** quick checks of the journeys people actually use: log in, get an MFA code, submit, pay.
- **Reopen and monitor:** watch error rates and support channels for the next few hours.
</details>

## Where it breaks

The buffer is sized for small surprises, not for a step that fails outright. These are the usual culprits:

<figure class="fig" id="figure-2">
{% include diagrams/where-it-breaks-wide.svg %}
{% include diagrams/where-it-breaks-narrow.svg %}
<figcaption>Figure 2 — Where it breaks. Amber "!" means slow or degraded; red "✕" means blocked.</figcaption>
</figure>

One of these adds hours. Two or three together add days.

<details class="deep" markdown="1">
<summary>Deep dive: the failure points in detail</summary>

- **Config drift:** production quietly stops matching test. A secret rotated by hand, an expired TLS certificate (the file that lets browsers trust the site), a firewall rule that only exists in one place. On Azure App Service, settings can be marked as *slot settings*, which stay with an environment during a swap; mark the wrong one and the new version points at the wrong database.
- **Slow migration:** see the next section.
- **Data corruption:** migrations touch every row, so they find years-old problems: duplicates, impossible dates, broken links between tables.
- **Failed smoke test / broken integration:** identity and MFA, SMS gateways, payments, email and registry lookups are each run by someone else, with their own credentials, rate limits and IP allow-lists.
- **Security finding:** a scan during the window finds something that must be fixed before reopening.
- **Organisational overhead:** in a large organisation every new fix is a new change, with approval, vendor tickets and sign-off.
</details>

## Why migrations get slow at production scale

A migration that ran in seconds on test data can take most of an hour on the real thing, and that's before anything goes wrong.

<figure class="fig" id="figure-3">
{% include diagrams/migration-costs-wide.svg %}
{% include diagrams/migration-costs-narrow.svg %}
<figcaption>Figure 3 — Same script, 100× the rows, 100× the time. Then four hidden costs on top.</figcaption>
</figure>

The fourth cost, locks, is the one that surprises even experienced teams. A schema change can freeze the whole site *before it has started*:

<figure class="fig" id="figure-4">
{% include diagrams/lock-queue-wide.svg %}
{% include diagrams/lock-queue-narrow.svg %}
<figcaption>Figure 4 — The lock queue. The ALTER waits for the report; every new query waits for the ALTER.</figcaption>
</figure>

<details class="deep" markdown="1">
<summary>Deep dive: rewrites, indexes, logs and locks (with SQL)</summary>

**Rewrites.** Some changes only update the database's catalogue (its record of what tables look like). In PostgreSQL 11+, adding a column with a constant default is one of those and finishes almost at once. A volatile default like `now()`, or changing a column's type, rewrites the whole table.

**Indexes.** A plain `CREATE INDEX` blocks writes while it reads and sorts the table. `CREATE INDEX CONCURRENTLY` doesn't, but it's slower, can't run inside a transaction, and if it fails it leaves an *invalid* index to drop and rebuild.

**Logs.** Every change is written to the transaction log first (the WAL in PostgreSQL). Millions of updated rows mean gigabytes of log, full disks and replicas (read-only copies) falling behind.

**Locks.** Most `ALTER TABLE` statements need an `ACCESS EXCLUSIVE` lock: nobody can even read the table. Waiting locks form a queue, so everything behind the `ALTER` waits too. The fix is to give up fast and retry:

```sql
-- PostgreSQL. If the lock isn't free within 3 seconds, cancel: the queue drains
-- and the migration tool retries a little later.
SET lock_timeout = '3s';

-- PG 11+: no default, so no table rewrite. Holds the lock only for a moment.
ALTER TABLE applicant ADD COLUMN mobile_e164 varchar(16);

-- Doesn't block writes, but must run outside a transaction block.
-- If it fails, drop the INVALID index it leaves behind and run it again.
CREATE INDEX CONCURRENTLY idx_applicant_mobile ON applicant (mobile_e164);
```

**Can you cancel half-way?** In PostgreSQL, cancelling a transaction is near-instant; `VACUUM` cleans up later. In SQL Server without Accelerated Database Recovery (ADR), undoing can take about as long as the work already done. Azure SQL Database always has ADR on, so rollback of a cancelled transaction is near-instant. On every engine, batches that already committed stay committed.
</details>

## Rolling back: code is easy, data is hard

Code has no memory: redeploy yesterday's version and it behaves like yesterday. A database remembers everything written since the change.

<figure class="fig" id="figure-5">
{% include diagrams/code-vs-data-rollback-wide.svg %}
{% include diagrams/code-vs-data-rollback-narrow.svg %}
<figcaption>Figure 5 — Code vs. data rollback. RPO is how much data you can afford to lose; RTO is how long you can afford to be down.</figcaption>
</figure>

**A real example.** In January 2017, GitLab accidentally deleted about 300 GB from its production database. Its regular backups turned out not to work. It restored from a copy an engineer had happened to take six hours earlier, and copying it back took around 18 hours on slow disks. About six hours of data were lost. GitLab published a [very open postmortem](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/), and its lesson is simple: a backup you haven't restored isn't a backup.

<details class="deep" markdown="1">
<summary>Deep dive: what an irreversible migration looks like</summary>

A realistic change: store phone numbers in one international format, so SMS codes send reliably.

```sql
-- One release, one step. Simple to write, impossible to undo safely.
ALTER TABLE applicant ADD COLUMN mobile_e164 varchar(16);

-- Rewrites every row in one transaction: slow on millions of rows.
-- normalise_phone() stands in for your own conversion function.
UPDATE applicant SET mobile_e164 = normalise_phone(phone);

-- The point of no return. The old app version still reads "phone" and breaks at once,
-- and a "down" migration can't rebuild the original values from the converted ones.
ALTER TABLE applicant DROP COLUMN phone;
```

If the new SMS integration then fails, you can't redeploy the old version: its column is gone. Your only routes are fix forward or restore.
</details>

## Restore or repair?

Restoring a backup over production also deletes the good work done since. Experienced teams often prefer to repair just the damaged rows.

<figure class="fig" id="figure-6">
{% include diagrams/restore-options-wide.svg %}
{% include diagrams/restore-options-narrow.svg %}
<figcaption>Figure 6 — Full restore vs. surgical repair. A repair keeps every good write, at the cost of more care.</figcaption>
</figure>

<details class="deep" markdown="1">
<summary>Deep dive: point-in-time restore and a surgical repair in SQL</summary>

Most production databases combine **full**, **differential** and **transaction-log** backups. Replaying the log lets you restore to an exact moment, say one minute before the migration: a *point-in-time restore* (PITR). Three costs bite during an outage:

1. Restore time grows with database size and log volume. Your real RTO is whatever that takes; rehearse it.
2. It often creates a new database. Azure SQL Database restores a point in time into a *new* database (history kept 1–35 days, 7 by default), so every connection string must be repointed mid-incident.
3. A full restore throws away everything written since that moment.

A surgical repair restores the backup *alongside* production and copies back only what was damaged. Using the irreversible example above:

```sql
-- PostgreSQL. restored_applicant was copied in from a point-in-time restore
-- taken just before the migration ran.
ALTER TABLE applicant ADD COLUMN phone varchar(32);   -- bring the old column back

UPDATE applicant AS live
SET    phone = r.phone
FROM   restored_applicant AS r
WHERE  r.id = live.id;

-- Applicants created after the migration have no "before" value: check by hand.
SELECT id FROM applicant WHERE phone IS NULL AND mobile_e164 IS NOT NULL;
```
</details>

## What a restore can't undo

Emails already sent, cards already charged, records already passed on. The fix is to record every side effect in the database *first*.

<figure class="fig" id="figure-7">
{% include diagrams/side-effects-wide.svg %}
{% include diagrams/side-effects-narrow.svg %}
<figcaption>Figure 7 — The outbox pattern and idempotency keys make side effects traceable and retry-safe.</figcaption>
</figure>

<details class="deep" markdown="1">
<summary>Deep dive: outbox, idempotency keys and reconciliation SQL</summary>

**Outbox.** Save the business change and the *intention* to send in one transaction; a worker does the sending.

```sql
BEGIN;
UPDATE application SET status = 'submitted' WHERE id = 42;
INSERT INTO outbox (event_id, kind, payload)
VALUES (gen_random_uuid(), 'submission_email', '{"application_id": 42}');
COMMIT;  -- both rows are saved, or neither: no email for a submission that didn't happen
```

**Idempotency keys.** A timeout doesn't tell you whether a payment went through. Send a unique key with each payment request; providers such as Stripe return the original result for a repeated key (within 24 hours) instead of charging again.

**Reconcile** the provider's records against your restored database:

```sql
-- provider_payments: the payment provider's export for the incident window.
-- Charged at the provider, but missing from our database: refund or re-create.
SELECT p.provider_payment_id, p.amount, p.created_at
FROM   provider_payments AS p
LEFT JOIN payment AS d ON d.provider_payment_id = p.provider_payment_id
WHERE  d.provider_payment_id IS NULL;
```

**Sessions and caches** are the subtle case: if the new version saved session data in a new format, the old one may not read it. Put the release version in cache keys and force a fresh login after a rollback.
</details>

## Roll back or fix forward?

This one decision often sets whether an outage lasts hours or days. The key question is the second one: **can the old code still run against the new database?**

<figure class="fig fig-sm" id="figure-8">
{% include diagrams/rollback-decision-tree-wide.svg %}
{% include diagrams/rollback-decision-tree-narrow.svg %}
<figcaption>Figure 8 — Rollback decision tree. Green "✓" low risk, amber "!" medium risk, red "✕" data loss possible.</figcaption>
</figure>

## How a short window can become days (hypothetical)

No single step takes three days. The time comes from waiting, on a slow migration, a vendor, a decision or an approval, and each wait is reasonable on its own. **This timeline is an illustrative example, not based on any real organisation.**

<figure class="fig" id="figure-9">
{% include diagrams/three-day-outage-wide.svg %}
{% include diagrams/three-day-outage-narrow.svg %}
<figcaption>Figure 9 — A hypothetical three-day outage across four swimlanes. Illustrative only.</figcaption>
</figure>

## How teams keep maintenance short

The goal isn't zero failures. It's keeping each failure small and "undo" cheap. Two patterns do most of the work.

**Blue-green deployment:** run two environments and switch traffic between them. Rollback is flipping the switch back. (On Azure App Service, *deployment slots* provide this built in. I don't know how the permits portal itself is deployed.)

<figure class="fig" id="figure-10">
{% include diagrams/big-bang-vs-blue-green-wide.svg %}
{% include diagrams/big-bang-vs-blue-green-narrow.svg %}
<figcaption>Figure 10 — Big-bang vs. blue-green. Both environments share one database, so the schema must suit both versions.</figcaption>
</figure>

**Expand/contract migrations:** because blue and green share a database, split each risky schema change into steps the old code can live with.

<figure class="fig" id="figure-11">
{% include diagrams/expand-contract-wide.svg %}
{% include diagrams/expand-contract-narrow.svg %}
<figcaption>Figure 11 — Expand/contract. Until the last release, rollback is just a code rollback.</figcaption>
</figure>

<details class="deep" markdown="1">
<summary>Deep dive: expand/contract in SQL</summary>

```sql
-- Release 1: EXPAND. Add the new column, nullable, so old code is unaffected.
SET lock_timeout = '3s';
ALTER TABLE applicant ADD COLUMN mobile_e164 varchar(16);
-- The app now writes BOTH columns on every save.
-- Backfill old rows in small id ranges, outside peak hours. Repeat with the next range.
-- "AND mobile_e164 IS NULL" makes it safe to stop and re-run.
UPDATE applicant
SET mobile_e164 = normalise_phone(phone)
WHERE id BETWEEN 1 AND 5000
  AND mobile_e164 IS NULL;

-- Release 2: MIGRATE. The app READS mobile_e164 and still writes both.
-- Before moving on, prove the new column is complete and correct. Must return 0.
SELECT count(*) FROM applicant
WHERE  mobile_e164 IS DISTINCT FROM normalise_phone(phone);

-- Release 3: CONTRACT. Weeks later, once nothing reads "phone",
-- after a fresh, tested backup:
ALTER TABLE applicant DROP COLUMN phone;
```
</details>

Four more habits round it out:

- **Feature flags:** switch a new code path off without deploying.
- **Rehearse the undo:** run the down migration and a real restore on production-sized data, and time it. That's your honest RTO.
- **Watch user journeys, not servers:** can someone log in, get an MFA code, submit and pay?
- **Regular status updates:** what's affected, what still works, and when the next update is due.

<details class="deep" markdown="1">
<summary>Deep dive: a feature flag and a deep health check (Python)</summary>

```python
import zlib

# Percentage of users who get each new feature. Set it to 0 to "roll back" with no deployment.
FLAGS = {"new_mfa_provider": 5}

def enabled(flag: str, user_id: str) -> bool:
    # A stable hash, so each user stays in the same group on every request.
    bucket = zlib.crc32(f"{flag}:{user_id}".encode()) % 100
    return bucket < FLAGS.get(flag, 0)
```

A health check that tests each dependency a user journey needs:

```python
import time

import psycopg
import requests
from flask import Flask, jsonify

app = Flask(__name__)
DB_URL = "postgresql://health_ro@db/permits"         # a read-only health-check user
SMS_STATUS = "https://sms-provider.example/status"   # your providers' real status endpoints
PAYMENTS_STATUS = "https://payments.example/health"


def database():
    with psycopg.connect(DB_URL, connect_timeout=2) as conn:
        conn.execute("SELECT 1")


def sms_mfa():
    requests.get(SMS_STATUS, timeout=2).raise_for_status()


def payments():
    requests.get(PAYMENTS_STATUS, timeout=2).raise_for_status()


def run(check):
    start = time.monotonic()
    try:
        check()
        status = "ok"
    except Exception as e:  # report the failure type, not the details: this endpoint may be public
        status = f"fail ({type(e).__name__})"
    return {"status": status, "ms": round((time.monotonic() - start) * 1000)}


@app.get("/health/deep")
def deep_health():
    checks = {"database": run(database), "sms_mfa": run(sms_mfa), "payments": run(payments)}
    healthy = all(c["status"] == "ok" for c in checks.values())
    return jsonify(status="ok" if healthy else "degraded", checks=checks), 200 if healthy else 503
```

Don't point the load balancer's liveness check (the probe that decides whether a server gets traffic) at this endpoint. A one-minute SMS blip should raise an alert, not pull every server out of service.
</details>

## Why it matters for public services

Behind every maintenance page are people with start dates, renewals and appointments, and an engineering team usually working flat out to bring the service back safely. Downtime can't always be avoided. What engineering can do is keep each change small, keep the undo cheap, and make an honest estimate easy to give.

I've spent about ten years building ETL pipelines (jobs that move and reshape data between systems) and moving production databases, including [migrating SQL Server to Azure SQL](/blog/azure-sql-migration-25-percent/). The hardest part was never the code. It was the data.

## Sources

- Employment Permits Online, [homepage](https://employmentpermits.enterprise.gov.ie/) and an [indexed copy of the login page](https://employmentpermits-prod.azurewebsites.net/portal-login) (scheduled 6pm–9pm outage notice).
- Law Society Gazette, ["Cloud-based work permit portal will work on e-sigs"](https://lawsociety.ie/gazette/top-stories/2025/april/cloud-based-work-permit-portal-will-work-on-e-sigs) (April 2025).
- Fragomen, ["Ireland: New Employment Permit Application Platform Launched"](https://www.fragomen.com/insights/ireland-new-employment-permit-application-platform-launched.html).
- Irish Statute Book, [S.I. No. 172/2025](https://www.irishstatutebook.ie/2025/en/si/0172.html): the department's change of name to Enterprise, Tourism and Employment.
- GitLab, ["Postmortem of database outage of January 31"](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/) (10 February 2017).
- AWS Well-Architected Reliability Pillar, ["Recovery Time Objective (RTO) and Recovery Point Objective (RPO)"](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/recovery-time-objective-rto-and-recovery-point-objective-rpo.html).
- PostgreSQL documentation, ["Explicit Locking"](https://www.postgresql.org/docs/current/explicit-locking.html) and ["CREATE INDEX"](https://www.postgresql.org/docs/current/sql-createindex.html).
- Microsoft Learn, ["Restore a database from a backup – Azure SQL Database"](https://learn.microsoft.com/en-us/azure/azure-sql/database/recovery-using-backups?view=azuresql), ["Accelerated Database Recovery"](https://learn.microsoft.com/en-us/sql/relational-databases/accelerated-database-recovery-concepts) and ["Set up staging environments in Azure App Service"](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots).
- Stripe, ["Idempotent requests"](https://docs.stripe.com/api/idempotent_requests).
- Chris Richardson, ["Pattern: Transactional outbox"](https://microservices.io/patterns/data/transactional-outbox.html).
- Martin Fowler, ["Blue Green Deployment"](https://martinfowler.com/bliki/BlueGreenDeployment.html) and ["Parallel Change"](https://martinfowler.com/bliki/ParallelChange.html) (the expand/contract pattern).

## Update log

- **27 October 2026:** First published. The portal had been showing its "essential maintenance" page for about three days. The reason has not been shared publicly.
