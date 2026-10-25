---
title: "Gmail auto-reply with Telegram approval"
summary: "Claude drafts a reply to each new email; nothing is sent until I tap ✅ on Telegram."
problem: "Routine emails take time, but an AI that sends email on its own can misunderstand or be manipulated."
approach: "Claude drafts a reply as a Gmail draft and sends it to Telegram with Send and Discard buttons."
result: "A routine reply becomes one tap, and the AI never sends anything by itself."
description: "A Python assistant by Malav Naik that uses Claude to draft Gmail replies, saves them as drafts and sends them only after approval on Telegram."
order: 7
featured: true
code_url: https://github.com/malavnaik99/telegram-approval-bots
tech: [Python, Claude API, Gmail API, Telegram Bot API, Prompt engineering]
---
## The problem
Replying to routine emails takes time, but letting an AI send emails on its own is a bad idea: it can misunderstand, promise things I didn't agree to, or be manipulated by the email itself.

## What I built
An assistant that reads my new Primary-inbox emails, asks Claude to draft a reply in my voice, and saves it as a **Gmail draft**. It then sends me the email and the draft on Telegram with **✅ Send** and **❌ Discard** buttons. Nothing leaves my inbox until I tap Send – and I can still edit the draft in Gmail first.

## How it works

<svg viewBox="0 0 640 230" role="img" aria-labelledby="gm-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="14">
  <title id="gm-title">Flow: new email, Claude drafts a reply, the draft is saved in Gmail, Telegram asks for approval, then the draft is sent or deleted</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="10" y="20" width="140" height="44" rx="8"/><rect x="170" y="20" width="140" height="44" rx="8"/>
    <rect x="330" y="20" width="140" height="44" rx="8"/><rect x="490" y="20" width="140" height="44" rx="8"/>
    <rect x="390" y="160" width="110" height="44" rx="8"/><rect x="520" y="160" width="110" height="44" rx="8"/>
    <path d="M150 42h16M310 42h16M470 42h16M560 64v50H445v42M560 114v42"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="80" y="47">New email</text><text x="240" y="47">Claude drafts</text>
    <text x="400" y="47">Gmail draft</text><text x="560" y="47">Telegram ✅ / ❌</text>
    <text x="445" y="187">✅ Sent</text><text x="575" y="187">❌ Deleted</text>
  </g>
</svg>

1. **Checks Gmail** for unread Primary-inbox mail. Newsletters, receipts and `noreply` senders get no draft (the model answers `SKIP`).
2. **Claude drafts the reply** with a short system prompt: my voice, short and friendly, no invented facts, prices or dates.
3. **Prompt-injection guard:** the email is treated as untrusted data. The model is told to reply to it, never to follow instructions inside it.
4. **Saves a threaded Gmail draft** and sends the email plus the draft to Telegram with buttons.
5. **Only my chat can approve.** Taps from anyone else are ignored; ✅ sends the draft, ❌ deletes it.

## Demo
<img src="{{ '/images/projects/gmail-bot-demo.gif' | relative_url }}" alt="Animated illustration of the Telegram chat: a fake email from Anna asking for a coffee chat, Claude's draft reply, and the Send button being tapped, then 'Sent'" width="360" height="640" loading="lazy">

*An illustration with a fake example email.*

## Results
- Built and tested end to end: a routine reply becomes one tap instead of writing it from scratch.
- Every email still gets a human decision – the AI never sends anything by itself.
- Unit tests cover email parsing and correct reply threading.

## What I learned
- **Treat inputs as untrusted.** An email can contain instructions aimed at the AI; the prompt has to say clearly that it's data, not commands.
- **Drafts are the right safety net.** Saving to Gmail Drafts means I can always edit before sending, and nothing is lost if the bot stops.
- **Small, boring code wins.** A few functions, standard libraries and one shared Telegram helper are easy to trust and to test.
