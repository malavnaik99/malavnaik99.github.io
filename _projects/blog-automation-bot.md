---
title: "Blog automation bot with Telegram approval"
summary: "Writes nothing until I approve on Telegram, then publishes each post to my blog, DEV and LinkedIn – running for free on GitHub Actions."
description: "A Python bot by Malav Naik that sends weekly blog post previews to Telegram and, only after approval, publishes to GitHub Pages, DEV and LinkedIn via their APIs using GitHub Actions."
order: 5
featured: true
code_url: https://github.com/malavnaik99/telegram-approval-bots
tech: [Python, GitHub Actions, Telegram Bot API, DEV (Forem) API, LinkedIn Posts API, Jekyll]
---
## The problem
I wanted to publish two posts a week on my own site and cross-post them to DEV, LinkedIn and Medium. Doing that by hand means copying text, uploading photos and fixing links four times per post. But fully automatic posting is risky: nothing should go public under my name without me seeing it first.

## What I built
A bot that does all the publishing work and **waits for one tap from me**. Every Monday at 9:00 it sends me previews of my next two posts on Telegram. When I tap ✅, it publishes the post to this blog, then to DEV and LinkedIn, and sends me the 30-second Medium import steps. When I tap ❌, the post waits until next week.

## How it works

<svg viewBox="0 0 640 400" role="img" aria-labelledby="bb-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="14">
  <title id="bb-title">Flow: post files go to a Telegram preview; after approval GitHub Actions publishes to the blog, then DEV and LinkedIn, and sends Medium steps</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="200" y="10" width="240" height="44" rx="8"/><rect x="200" y="90" width="240" height="44" rx="8"/>
    <rect x="200" y="170" width="240" height="44" rx="8"/><rect x="200" y="250" width="240" height="44" rx="8"/>
    <rect x="10" y="340" width="140" height="44" rx="8"/><rect x="170" y="340" width="140" height="44" rx="8"/>
    <rect x="330" y="340" width="140" height="44" rx="8"/><rect x="490" y="340" width="140" height="44" rx="8"/>
    <path d="M320 54v32M320 134v32M320 214v32M320 294v20M80 314h480M80 314v22M240 314v22M400 314v22M560 314v22"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="320" y="37">Post files (Markdown)</text>
    <text x="320" y="117">Monday: Telegram preview ✅ / ❌</text>
    <text x="320" y="197">GitHub Actions (every 15 min)</text>
    <text x="320" y="277">Blog live? (waits for HTTP 200)</text>
    <text x="80" y="367">My blog</text><text x="240" y="367">DEV</text>
    <text x="400" y="367">LinkedIn</text><text x="560" y="367">Medium steps</text>
  </g>
</svg>

1. **Posts are plain Markdown files** with front matter (title, tags, photo, where to post, status). Only posts I've marked `ready` – and with no open fact-check note – are offered.
2. **A GitHub Actions workflow runs every 15 minutes.** It reads Telegram button taps (only from my own chat; anyone else's taps are ignored) and on Mondays sends the week's previews.
3. **On ✅ it publishes to my blog first** by committing the post to this GitHub Pages site, then **waits until the page actually loads** before posting anywhere else, so the links never point to a missing page.
4. **DEV** gets the full article with my blog as the canonical (original) source. **LinkedIn** gets a short post with the photo, an intro and the link, through LinkedIn's official Posts API.
5. **Never twice:** after each platform succeeds, the bot writes the URL into the post file and commits it straight away. A re-run skips whatever is already done, and a failure on one platform is reported to me in plain words while the others carry on.
6. **LinkedIn logins expire every ~60 days.** The bot reminds me a week before; I log in through a small page on this site and send the code to the bot, which stores the new token securely as a GitHub secret.

## Demo
<img src="{{ '/images/projects/blog-bot-demo.gif' | relative_url }}" alt="Animated illustration of the Telegram chat: a post preview, the Post button being tapped, then confirmations for the blog, DEV and LinkedIn, the Medium steps and a status table" width="360" height="640" loading="lazy">

*An illustration of the real flow, recreated with example content.*

## Results
{% include automation-lab.html %}

- In use since October 2026: posts going out to [this blog]({{ '/blog/' | relative_url }}), [DEV](https://dev.to/malavnaik_0381711024683d4), LinkedIn and Medium, with one tap each.
- 50 posts queued at two a week; each one takes me about a minute (one tap, plus the Medium import) instead of copying, pasting and re-uploading it on four sites.
- Runs entirely on GitHub's free tier – no server, nothing to keep switched on.
- 10 automated tests cover post selection, the blog transformation, the never-twice rule, LinkedIn text escaping and login reminders; they run before every bot run.

## What I learned
- **Human approval is a feature, not a limitation.** One tap keeps me in control while the bot does almost all of the work.
- **Record progress immediately.** Writing each platform's result before moving on is what makes re-runs safe.
- **Use official APIs.** LinkedIn and DEV both offer them; browser automation would break their terms and risk the account.
