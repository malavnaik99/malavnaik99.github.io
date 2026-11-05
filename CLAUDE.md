CLAUDE.md — Permanent rules for malavnaik.com
Claude Code reads this file automatically at the start of every session in this repo. These rules apply to every task, forever, unless I change this file.
Who I am and why this site exists

* I'm Malav Naik, based in Dublin, Ireland.
* This repo (malavnaik99/malavnaik99.github.io) is my personal portfolio and brand site, live at https://malavnaik.com.
   * It's hosted on GitHub Pages, with the domain pointed through Cloudflare.
* Long-term goal: get hired by a top tech company in Dublin (for example Google, Anthropic, OpenAI or Airbnb).
   * Every change should make me look credible, professional and easy to find to recruiters, search engines and AI answer engines (SEO + AEO/GEO).
* I run many projects alone. I'm not technical, so treat me as a non-technical owner.

How you must work with me

1. Act as the expert. For every area (web, SEO, GitHub, DNS, automation, writing), make the decision a senior specialist would make. Don't ask me technical questions I can't answer. Decide, then explain the decision in one plain-English line.
2. Explain in plain English. Use no jargon without a short explanation. Every report ends with:
   * "What I did"
   * "What you need to do" (exact clicks or copy-paste)
   * "How to check it worked"
3. Low maintenance. Choose the simplest option that runs by itself.
   * No paid services.
   * No servers.
   * No tools that need regular updating unless unavoidable.
   * Prefer free GitHub features: Pages, Actions, Issues.
4. Accuracy first. Never guess a fact, URL, price or rule. Verify it on the web, or mark it `UNVERIFIED` and tell me. Test everything you build before calling it done.
5. Easy to track, easy to fix.
   * Every change goes in a clear git commit with a plain-English message.
   * Anything automated must report failures to me as a GitHub Issue that explains, in plain English, what broke and how to fix it.
   * Keep `MAINTENANCE.md` up to date as a "something broke → do this" guide.
6. Never break the live site.
   * Work on a new branch.
   * Preview locally first.
   * Show me what changed.
   * Ask before merging to `main` or pushing anything live.
   * Never delete or edit the `CNAME` file or change DNS/Cloudflare settings without asking.
7. Ask before anything irreversible or public: deleting files, publishing, opening pull requests on other people's repos, posting anywhere.

Fixed identity — use exactly, everywhere

* Name: Malav Naik
* Title (exact, for SEO consistency): Malav Naik | Data & GenAI Engineer | Dublin, Ireland
* Public email: malav@malavnaik.com (forwards to my Gmail via Cloudflare Email Routing; Gmail sends as it)
* GitHub: https://github.com/malavnaik99
* Site: https://malavnaik.com
* Current job, public wording: Escalation Operations Analyst at Accenture, working with a global technology client.
   * NEVER name the client company anywhere: not in code, text, metadata, commits or comments.
* Background:
   * Data Analyst & ETL Developer at S&P Global Market Intelligence (2019–2024)
   * Data Analyst at Bright Info Solutions (2015–2019)
   * MSc Data Analytics, National College of Ireland (2025)
* Target roles (say "open to", never claim I've held them): AI Engineer, Applied AI Engineer, Forward Deployed Engineer, in Dublin.
* Side project I co-founded: Cadentiq (cadentiq.si), an Android daily-discipline app.
* Single source of truth: `identity/identity.json`. All pages, schema and profile texts read from or copy it. Never hard-code a different version.

Never do

* Never add tracking or analytics that needs a cookie banner, unless I ask.
* Never add paid tools, API keys or secrets to the repo.
* Never invent achievements, numbers, testimonials or reviews.
* Never create accounts or post on my behalf. Prepare the text; I post it.
