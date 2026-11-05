# Something broke? Start here

Plain-English fixes for malavnaik.com. Each problem below comes with what it means and exactly what to do.
When in doubt, open Claude Code on this repo and paste what you see. Claude follows `CLAUDE.md`.

**How you hear about problems:** the **Site health** check runs every Monday at 07:00 (Irish time) and after every change.
If something is wrong it opens a GitHub Issue titled `Site health: …` (GitHub emails you if you **Watch** this repo),
updates it while the problem lasts, and closes it by itself once fixed. Issues: https://github.com/malavnaik99/malavnaik99.github.io/issues

## If you see this → it means → do this

| If you see this | It means | Do this |
|---|---|---|
| Issue **Site health: Site not loading** | malavnaik.com didn't open over HTTPS, or `http://` / `www.` stopped forwarding to it | 1. Wait 15 min, then **Actions → Site health → Run workflow** (outages often fix themselves). 2. **Settings → Pages**: *Custom domain* = `malavnaik.com` with a green tick, **Enforce HTTPS** ticked. 3. Still broken: send Claude a screenshot of Settings → Pages and of Cloudflare → DNS. Don't change DNS yourself. |
| Issue **Site health: Page title or profile data missing** | A page lost the exact title *Malav Naik \| Data & GenAI Engineer \| Dublin, Ireland* or its hidden "Person" profile data | Ask Claude: "Site health says the title or profile data is missing on these pages: (paste the list from the issue). Fix it." Or roll back the last change (bottom of this page). |
| Issue **Site health: Broken links** | A link on your site leads nowhere | Open the listed links. If really broken, ask Claude: "Fix these broken links: (paste list)". If it's one of your GitHub repos, check it's still **Public**. |
| Issue **Site health: Profile no longer links to malavnaik.com** | A profile marked `live` in `backlinks/tracker.csv` lost its website link or no longer loads | Sign in to that platform and put `https://malavnaik.com` back in the Website field. If you closed the account, change its tracker row to `rejected`. |
| Issue **Site health: CNAME file changed** | The file that tells GitHub to use malavnaik.com was changed or deleted | **Settings → Pages → Custom domain**: type `malavnaik.com` → **Save** (GitHub recreates the file). Don't touch Cloudflare. |
| Issue **Site health: Employer's client named in the repo** | Some file names your employer's client | Replace the name with *a global technology client* at each listed file/line, or ask Claude to. |
| Red ❌ on **Actions → Deploy site to Pages**, with "The site no longer matches identity/identity.json" | A change brought back the old title or old email, so the deploy stopped (the live site stays on the last good version) | Ask Claude: "The deploy failed with this message: (paste it)". The message lists the exact files. |
| Red ❌ on **Deploy site to Pages**, "Images without alt text" | A new image has no description for screen readers | Ask Claude to add alt text to the listed images. |
| Page says **"There isn't a GitHub Pages site here"** | The custom domain was removed from GitHub Pages | **Settings → Pages → Custom domain** → `malavnaik.com` → **Save**, tick **Enforce HTTPS** once it's available (can take up to an hour). |
| Browser says **"Your connection is not private"** | The HTTPS certificate has a problem (GitHub or Cloudflare side) | Wait an hour; then check **Settings → Pages** for a certificate message and send Claude screenshots of it and Cloudflare → SSL/TLS. Don't change Cloudflare without asking. |
| Email to **malav@malavnaik.com** stops arriving | Cloudflare Email Routing is off or its DNS records changed | Cloudflare → **Email Service → Email Routing**: status must be *Enabled* and the `malav` rule must point to your Gmail. Send Claude a screenshot if not. |
| Replies from malav@malavnaik.com fail or land in spam | The Gmail App Password was revoked, or the SPF record changed | Gmail → Settings → **Accounts and Import** → *Send mail as* → **edit info** → new App Password from https://myaccount.google.com/apppasswords. |
| **No Site health run on a Monday** | GitHub pauses scheduled workflows in public repos after **60 days with no activity** | **Actions → Site health → Enable workflow**, then **Run workflow**. (The weekly blog bot normally keeps the repo active.) |
| A shared link shows the **old preview image/title** on LinkedIn | LinkedIn cached the old preview | https://www.linkedin.com/post-inspector/ → paste the URL → **Inspect** (refreshes it). |

## Roll back a bad change

**Fastest, one step (puts the old version live in about 2 minutes):**
1. Go to **Actions → Deploy site to Pages**.
2. Click the last run with a green ✅ **before** the bad change.
3. Click **Re-run all jobs**. GitHub republishes that older version.

This is temporary: the next change to `main` publishes the newest version again. So then tell Claude:
"Roll back the change called '(commit message)' on main", and it will undo it properly (a *revert* commit, so nothing is lost).

## Where things live (for Claude or a developer)
- Identity (name, title, email, bios, profiles): `identity/identity.json`, the single source of truth. `scripts/check_identity.py` stops a deploy that drifts from it.
- Page head, previews, structured data: `_layouts/default.html`, `_includes/schema.html`, `_config.yml`
- Health check: `.github/workflows/site-health.yml` + `scripts/site_health.py` (`python3 scripts/site_health.py` runs it locally)
- Backlinks: `backlinks/README.md` (kit), `backlinks/tracker.csv`, `backlinks/ROUTINE.md`
