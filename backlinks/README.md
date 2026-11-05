# Backlink kit: where to put malavnaik.com, and what to paste

Prepared by Claude, checked on 5 Nov 2026. **You post everything yourself; Claude never creates accounts or posts for you.**
All texts below are copied from `identity/identity.json`. If a fact changes, change it there first, then here.

## Read this first (2 minutes)

- **What this really does.** Most profile sites mark your link as *nofollow* (a label that tells Google "don't count this as a vote"). So these links won't push your ranking much on their own. What they *do* is:
  1. make the search results for "Malav Naik" fill up with **your** profiles, all saying the same thing;
  2. let Google and AI assistants connect those profiles to malavnaik.com and to each other (your site already lists them as "same person" in its hidden profile data);
  3. bring recruiters who find you on those sites to your portfolio.
- **Quality over quantity.** Google treats mass-creating profiles just for links as spam. Below are only reputable, relevant sites, in order of value. Do 1–2 a week (see `ROUTINE.md`).
- **Same words everywhere.** Use the exact name **Malav Naik**, headline **Data & GenAI Engineer**, and link **https://malavnaik.com**.
- **Your photo:** use the same professional photo everywhere: `images/malav-naik-portrait.jpg` in this repo.
- After each one, update `tracker.csv` (how: see `ROUTINE.md`). When a row says `live`, the weekly health check will confirm the link is still there.

`UNVERIFIED` means I couldn't confirm it from the platform's own pages (many of them block automated checks). Treat it as likely, not certain.

## The copy-paste texts

**Name:** `Malav Naik`

**Headline:** `Data & GenAI Engineer · Dublin, Ireland`

**Website:** `https://malavnaik.com`

**Short bio** (139 characters; fits any 160-character field):
```
Data & GenAI Engineer in Dublin. About 10 years in data: SQL and ETL pipelines, Azure SQL, dbt, and LLM tools that are tested and measured.
```

**Medium bio, first person** (249 characters; for "About" fields):
```
I'm Malav Naik, a Data & GenAI Engineer in Dublin with about 10 years in data. I built ETL pipelines at S&P Global Market Intelligence, hold an MSc in Data Analytics, and build tested GenAI and AI automation tools. Open to AI Engineer roles.
```

**Long bio, first person** (for long "About" sections):
```
I'm Malav Naik, a Data & GenAI Engineer in Dublin, Ireland, with about 10 years of experience in data. At S&P Global Market Intelligence (2019–2024) I built SSIS pipelines for financial data and helped migrate on-premise SQL Server to Azure SQL, cutting infrastructure costs by about 25%. I hold an MSc in Data Analytics from National College of Ireland, with a thesis on knowledge graphs and prompt engineering. I now work as an Escalation Operations Analyst at Accenture, with a global technology client. My public projects include a tested dbt and DuckDB data pipeline, a content moderation classifier with fairness checks, and LLM tools that act only after human approval. I'm open to AI Engineer, Applied AI Engineer and Forward Deployed Engineer roles in Dublin. Portfolio: https://malavnaik.com
```

**Skills (comma list):** `SQL, Python, dbt, DuckDB, Azure SQL, SSIS, Power BI, LLMs, RAG, Knowledge graphs, Prompt engineering, Claude API, Hugging Face, PyTorch, GitHub Actions`

Never mention the name of Accenture's client anywhere. "A global technology client" is the only wording.

---

## 1. LinkedIn: update (≈10 min) · highest value
You already have this account. LinkedIn is usually the first result for a person's name.
1. Open https://www.linkedin.com/in/malav-naik → click the pencil next to your name.
2. **Headline:** start it with `Data & GenAI Engineer · Dublin, Ireland`. You can keep extra words after it.
3. Scroll to **Contact info** → pencil → **Website** → **Add website** → URL `https://malavnaik.com`, type **Portfolio** → **Save**.
4. On your profile, **Add section → Recommended → Add featured → Add a link** → `https://malavnaik.com` → **Add**.
5. **About:** paste the long bio.
6. Optional: **Open to → Finding a new job** → job titles *AI Engineer*, *Applied AI Engineer*, *Forward Deployed Engineer* → location *Dublin* → visibility **Recruiters only** (so your current employer isn't shown it).
- Link type: `UNVERIFIED` (LinkedIn pages block automated checks).
- Tracker: set `link_to_malavnaik_live` = yes, `status` = live.

## 2. GitHub: website field + profile README (≈15 min)
GitHub is the first place technical recruiters look.
**A. Website and bio**
1. https://github.com/settings/profile
2. **Name:** `Malav Naik` · **Bio:** paste the short bio (GitHub allows 160 characters) · **URL:** `https://malavnaik.com` · **Company:** `Accenture` · **Location:** `Dublin, Ireland`
3. Under **Social accounts**, add your LinkedIn, Hugging Face and Kaggle links → **Update profile**.

**B. Profile README** (a welcome box at the top of your GitHub profile)
1. https://github.com/new → **Repository name:** `malavnaik99` (exactly your username) → **Public** → tick **Add a README file** → **Create repository**.
2. Click the pencil on `README.md`, delete everything, paste the whole of `backlinks/github-profile-README.md` from this repo → **Commit changes**.

**C. This website's repo**
1. https://github.com/malavnaik99/malavnaik99.github.io → the ⚙️ next to **About** (right side) → **Website:** `https://malavnaik.com` → **Save changes**.
- Link type: GitHub profile links are reported as nofollow (`UNVERIFIED`).

## 3. Hugging Face: fix (≈5 min)
I checked your profile on 5 Nov 2026: its website link still points to the **old address malavnaik99.github.io**, and your name shows as **"Malav naik"** (small n).
1. https://huggingface.co/settings/profile
2. **Full name:** `Malav Naik` · **Homepage:** `https://malavnaik.com` · **AI & ML interests:** `Data engineering, RAG, LLM evaluation, content moderation, knowledge graphs`
3. Bio, if there's a field: paste the short bio → **Save**.
- Link type: **nofollow** (checked on the page itself).

## 4. Kaggle: update (≈5 min)
1. https://www.kaggle.com/malavnaik → **Edit Public Profile**.
2. **Occupation / title:** `Data & GenAI Engineer` · **Location:** `Dublin, Ireland`
3. **Bio:** paste the medium bio. **Website / links:** add `https://malavnaik.com`, GitHub, LinkedIn → **Save**.
- Link type: `UNVERIFIED`. Your datasets and notebooks already link to the site, which helps more than the profile field.

## 5. Peerlist: profile (≈20 min)
A professional profile site for developers. The profile is free.
1. https://peerlist.io → **Sign up** with GitHub or Google. Claim the username `malavnaik` if it's free.
2. **Headline:** `Data & GenAI Engineer · Dublin, Ireland` · **Bio:** medium bio · **Website:** `https://malavnaik.com`
3. **Work:** add Accenture (Escalation Operations Analyst), S&P Global Market Intelligence, Bright Info Solutions. **Education:** National College of Ireland.
4. **Get verified (needed for Launchpad):** Profile → **Verification** → use **Workplace** or **Education** verification, which Peerlist's help centre says is free. Identity verification (with an ID) costs a one-off fee: skip it.
5. **Projects:** add 2–3 projects with the links from `github-profile-README.md`.
- Link type: third-party sites say Peerlist profile links are nofollow (`UNVERIFIED`).
- Sources: [Peerlist verification](https://help.peerlist.io/individual/peerlist-profile/verification), [identity verification](https://help.peerlist.io/individual/peerlist-profile/verification/identity).

## 6. DEV (dev.to): update (≈5 min)
You already post here through the blog bot, with a "canonical" link pointing to your site (which tells Google your site is the original).
1. https://dev.to/settings → **Name:** `Malav Naik` · **Website URL:** `https://malavnaik.com` · **Bio:** short bio · **Location:** `Dublin, Ireland` · **Work:** `Escalation Operations Analyst at Accenture` → **Save**.
- Link type: sources disagree (`UNVERIFIED`).
- **First-article idea:** *How I test a €0 data pipeline: automatic dbt checks on Dublin bikes data*

## 7. Medium: update (≈5 min)
1. https://medium.com/me/settings → **Profile information** → **Name:** `Malav Naik` · **Short bio:** short bio (Medium's limit is 160 characters, per Medium's own guide).
2. Add `https://malavnaik.com` to the **About** section of your profile.
- Link type: reported nofollow (`UNVERIFIED`).
- **First-article idea:** *What escalation work taught me about deploying AI with real users*. This fits the Forward Deployed Engineer angle. Describe your work in general terms only and never name the client.

## 8. Hashnode: new (≈15 min)
After its June 2026 changes, Hashnode still has a free plan: one blog on a `hashnode.dev` address. Custom domains are now paid; you don't need one.
1. https://hashnode.com/onboard → sign up with GitHub → blog address `malavnaik.hashnode.dev`.
2. **Profile:** name, short bio, **Website** `https://malavnaik.com`.
3. When you cross-post, set the **original/canonical URL** to the post on malavnaik.com (in the article settings) so Google credits your site.
- Link type: `UNVERIFIED`. The free plan details come from a third-party guide, so treat them as `UNVERIFIED` too.
- **First-article idea:** *Keyword vs semantic vs hybrid search on the EU Digital Services Act: what 25 test questions showed*

## 9. ORCID: new (≈15 min) · extra I added
**Why it fits:** ORCID is the free, non-profit ID that researchers use worldwide. You have a published MSc thesis, so it's a trusted, permanent page that ties your name to that work and to your site.
1. https://orcid.org/register → name `Malav Naik`, email `malav@malavnaik.com`.
2. **Websites & social links** → pencil → add `https://malavnaik.com` (title: *Portfolio*) and LinkedIn.
3. **Biography:** long bio. **Employment:** Accenture. **Education:** National College of Ireland, MSc Data Analytics, 2025.
4. **Works → Add → Add manually** → type *Dissertation/Thesis* → title *Enhanced Personalized Learning Experiences by Leveraging Knowledge Graphs and Prompt Engineering* → year 2025 → link `https://norma.ncirl.ie/9439/`.
- Free: yes. Link type: `UNVERIFIED`.
- Once it exists, tell Claude the ORCID URL and it will be added to your site's "same person" links.

## 10. Stack Overflow: new (≈10 min, then only if you'll answer questions)
1. https://stackoverflow.com/users/signup → **Edit profile** → **Display name** `Malav Naik` · **Location** `Dublin, Ireland` · **Website link** `https://malavnaik.com` · **About me:** medium bio.
2. A profile with zero answers adds little. It's worth it if you answer 1–2 SQL, dbt or pandas questions a month.
- Link type: profile links reported nofollow (`UNVERIFIED`). Self-promotion rule: always say when a link is your own.

## 11. Wellfound: new (≈15 min)
Free for job seekers, per Wellfound's own help centre ([source](https://help.wellfound.com/article/799-does-angellist-cost-anything-for-job-seekers)). Mostly startup roles, including AI startups in Dublin.
1. https://wellfound.com/candidates → sign up → **Profile**: one-liner = headline, bio = medium bio, **Website** `https://malavnaik.com`, GitHub, LinkedIn.
2. **Preferences:** roles *AI Engineer*, *Data Engineer*; location *Dublin*; tick remote if you want it.
- Link type: `UNVERIFIED`.

## 12. Gravatar: new (≈5 min)
A free public profile tied to your email. Many sites (GitHub comments, WordPress, Slack tools) show your Gravatar photo automatically.
1. https://gravatar.com → sign up with **malav@malavnaik.com** → upload your portrait.
2. **About:** short bio · **Links:** add `https://malavnaik.com` → **Verified accounts:** connect GitHub (and others offered).
- Link type: `UNVERIFIED`.

## 13. Indie Hackers: for Cadentiq (≈15 min)
Founders' community. Put your link on your **Cadentiq** presence, not as a portfolio advert.
1. https://www.indiehackers.com → sign up → profile: name, short bio, website `https://malavnaik.com`.
2. Add **Cadentiq** as a product (website `https://cadentiq.si`) and list yourself as co-founder, if your co-founder agrees.
3. Post only genuine milestones or lessons from building Cadentiq.
- Free status and link type: `UNVERIFIED` (their site blocks automated checks).

## 14. Contra: optional (≈15 min) · low priority
A free profile for independent/freelance work (Contra's own page says the profile is free; Pro is optional). **Only worth doing if you'd accept freelance work**: a freelance profile can confuse recruiters about what you're looking for.
1. https://contra.com → sign up → headline, medium bio, website `https://malavnaik.com`, add 2–3 projects.

## 15. about.me: optional (≈10 min) · lowest priority
The free plan still exists (`about.me/yourname`); paid plans are optional. It adds little beyond the others, so do it last, if at all.
1. https://about.me → sign up → `about.me/malavnaik` → headline, short bio, button link `https://malavnaik.com`.

## 16. Reddit: r/dataengineering and r/datascience (community, not backlinks)
Reddit links don't help SEO, and self-promotion gets you banned. The value is being known as someone helpful. You already have u/malavnaik.

**The rules (check the sidebar yourself before any post; I couldn't read Reddit directly):**
- **Reddit-wide rule of thumb**, quoted in r/datascience's rules: for every 1 self-promotional post or comment, make at least 9 that aren't.
- **r/datascience:** questions about careers, getting into the field or portfolio feedback go in the pinned **weekly "Entering & Transitioning" thread**, not as new posts (from the subreddit's wiki, via a mirror; `UNVERIFIED` that it's current).
- **r/dataengineering:** a third-party summary (July 2026) says self-promotion is limited to about once a month and company ties must be disclosed (`UNVERIFIED`). Lessons-learned posts are welcome there; launch announcements aren't.

**Rule-compliant ways to take part:**
1. Answer 2–3 questions a week where you know the answer (SQL, SSIS-to-cloud migrations, dbt tests). No links.
2. Ask for feedback in the right place, saying it's your own work.

**Draft: comment for r/datascience's weekly Entering & Transitioning thread**
```
Looking for honest feedback on my portfolio as I move from data engineering towards AI engineering roles in Dublin.

Background: ~10 years in data (SQL/SSIS pipelines, an Azure SQL migration), MSc Data Analytics in 2025, now in an escalations/platform-integrity role.

Portfolio (my own site): https://malavnaik.com/work/

Specific questions:
1. For AI engineer / applied AI roles, is a project like a DistilBERT moderation classifier with fairness checks (ROC-AUC 0.957) still a useful signal, or do hiring managers now expect LLM app projects?
2. Is it better to show fewer, deeper projects or keep all 8?

Thanks, happy to return the favour on anyone's portfolio.
```

**Draft: text post for r/dataengineering** (only after checking the sidebar, at most once a month, and flair it as the rules say)
```
Title: What I learned testing a €0 pipeline: dbt + DuckDB on Dublin bike-share data

I built a small pipeline as a learning project and wanted to share what actually caught problems, since most tutorials skip testing.

Setup: a Python collector saves every Dublinbikes station every 15 minutes (append-only Parquet), and a daily dbt run on DuckDB builds a star schema with automatic data checks (freshness, volume, uniqueness).

What I learned:
- Freshness and volume checks caught more real problems than column-level tests.
- Keeping raw data append-only made every bad day re-runnable.
- [add 1–2 real lessons in your own words]

Disclosure: it's my own project; write-up and code here if useful: https://malavnaik.com/projects/dublin-bikes-pipeline/

What tests do you consider the minimum for a small pipeline like this?
```
Before posting, replace the lessons with ones you actually saw. Never post claims you can't back up.

## 17. Peerlist Launchpad: your projects (Mondays)
- **When:** launches run **every Monday** (UTC); a third-party guide says 00:00–23:59 UTC. You need a **verified** Peerlist profile (step 5). Launching is free; "featured" upgrades are paid, so skip them.
- **What to launch:** real, tryable projects, **not** your portfolio page. Peerlist removes spam and repeated launches.
- **Plan (one every 3–4 weeks):**
  1. Ask the EU Digital Services Act (tryable in the browser)
  2. Content moderation classifier demo (Hugging Face Space)
  3. SkillBot skills explorer
  4. Cadentiq, only if your co-founder agrees and it hasn't been launched there already
- Sources: [Peerlist launch guide](https://help.peerlist.io/individual/launchpad/how-to-launch-a-project-on-peerlist-launchpad), [rules](https://help.peerlist.io/individual/spotlight/guidelines-faqs). I couldn't open these pages directly (blocked), so the details come from search summaries.

**Draft: first launch (Ask the EU Digital Services Act)**
- **Project name:** `Ask the EU Digital Services Act`
- **Tagline:** `Plain-English search over the EU Digital Services Act`
- **Description:**
```
Type a question in everyday words and get the three articles of the EU Digital Services Act most likely to answer it, quoted and linked to the official text.

It never writes its own answer, only quotes the law, so every result can be checked. Before building the demo I wrote 25 test questions and compared keyword (BM25), semantic and hybrid search. The right article is in the top 3 for 84% of them (72% in the free in-browser version).

It runs entirely in your browser, so nothing you type is sent anywhere. Not legal advice.

Built with Python, sentence-transformers, BM25 and transformers.js; data and demo on Hugging Face.
```
- **Links:** demo `https://huggingface.co/spaces/Malavnaik/ask-the-dsa` · code `https://github.com/malavnaik99/eu-dsa-search` · write-up `https://malavnaik.com/projects/ask-the-dsa/`
- **Category:** AI / Developer tools
- **Images:** a screenshot of the demo with a question typed in.

## 18. Hacker News "Show HN": later, only for a finished project
**The rules** (from HN's official Show HN guidelines, read via search because the page is blocked here):
- A Show HN is for **something you made that people can try**.
- **Blog posts, sign-up pages, newsletters, lists and other reading material can't be Show HNs.** Your portfolio and articles don't qualify.
- If it isn't ready for people to try, don't post it yet.
- Title starts with `Show HN:`. Don't ask anyone to upvote or comment, which HN treats as voting manipulation.
- Be there to answer comments for the first few hours.

**No draft yet**, as agreed. When a project is finished and tryable (the DSA search may qualify once you're happy with it), ask Claude to draft one.

## 19. developer-portfolios (GitHub list)
A long-running community list of developer portfolios on GitHub ([emmabostian/developer-portfolios](https://github.com/emmabostian/developer-portfolios); active, last updated 5 Nov 2026). Claude prepares a one-line pull request in Phase 4 and asks you before sending it.

---
Sources used while checking: [Medium bio limit](https://blog.medium.com/you-are-your-storys-best-asset-fd70c7d8c32) · [Hashnode free plan after June 2026](https://www.poster.ly/guides/hashnode-guide) · [Wellfound: free for job seekers](https://help.wellfound.com/article/799-does-angellist-cost-anything-for-job-seekers) · [Contra: free profile](https://contra.com/how-it-works/independents) · [about.me free plan](https://www.gappsy.com/tools/about-me/) · [Show HN rules](https://news.ycombinator.com/showhn.html) · [r/dataengineering summary](https://www.threadotter.com/subreddit-rules/dataengineering) · [r/datascience wiki mirror](https://axebps-redlib.hf.space/r/datascience/wiki) · [profile links and link spam](https://theguidex.com/insights/profile-creation-sites)
