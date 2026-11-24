# Blog bot: picking up each "Dublin Bikes in numbers" edition

**Status: needs a one-time change in the blog bot's repo** (not this one). Until then, the bot does not see the
monthly editions, so they are not cross-posted to LinkedIn, DEV or Medium.

## Why

The bot only offers posts from its own queue folder (`blog/posts/` in the bot's repo). The monthly editions are made
in this repo, so they never reach that folder. They also can't be queued as they are: the site's edition post is built
from a template (`{% include bikes-edition.html %}`), and DEV would receive that template code instead of the tables.

## What this repo now provides

When an edition is published here (its post lands in `_posts/`), the **Share kit** workflow writes
`share-kits/YYYY-MM/blog-bot-post.md`: the same edition as plain Markdown (tables included), in the bot's queue
format, with:

- `status: ready`, the site's `slug`, title, description, tags and chart (`images/bikes-report/YYYY-MM.png`);
- `id: -YYYYMM` (negative, so it goes ahead of ordinary posts in the next Monday preview, and unique each month,
  because the bot matches Telegram taps by `id`);
- `linkedin_intro` written from that month's two most unusual findings.

Because the edition is already live on the site, the bot's "publish to blog" step finds it, does **not** write a
second copy, and only checks the page loads before cross-posting. You still approve every post with a ✅ tap.

## The change to make in the bot's repo

Open Claude Code on the bot's repo and paste:

> In `.github/workflows/blog.yml`, add this step after the step that sets the git user name, and before the unit
> tests. Then run the tests.

```yaml
      - name: Queue new Dublin Bikes editions prepared by the site (site/share-kits/*/blog-bot-post.md)
        run: |
          for f in site/share-kits/*/blog-bot-post.md; do
            [ -e "$f" ] || continue
            m=$(basename "$(dirname "$f")")
            dst="blog/posts/dublin-bikes-$m.md"
            [ -e "$dst" ] && continue  # already queued: the bot keeps its progress in its own copy
            cp "$f" "$dst"
            mkdir -p blog/images/bikes-report
            cp "site/images/bikes-report/$m.png" blog/images/bikes-report/
            git add "$dst" "blog/images/bikes-report/$m.png"
            git commit -qm "blog bot: queue Dublin Bikes in numbers $m"
          done
          git push -q
```

This was tested (24 Nov 2026) against the public copy of the bot (`malavnaik99/telegram-approval-bots`) with the
October 2026 kit: the edition was queued once (a second run skipped it), the bot offered it first, saw the post
already on the site, found the LinkedIn photo, and sent DEV plain Markdown with no template code; the bot's own
tests still passed. If your running copy of the bot differs from the public one, check the step still fits.

## Good to know

- **The October 2026 edition will be offered first** on the next Monday after the change, because its kit already
  exists. Tap ✅ to cross-post it, or see the next point.
- **❌ Skip only postpones a post a week** (that's how the bot works for every post). To drop an edition for good,
  in the bot's repo change `status: ready` to `status: draft` in `blog/posts/dublin-bikes-YYYY-MM.md`.
- Each edition takes one of the two weekly slots, so an ordinary post may move back a week.
