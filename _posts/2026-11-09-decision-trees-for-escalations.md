---
id: 8
title: "Designing Decision Trees for Escalations: Classifying Messy Cases Consistently"
slug: decision-trees-for-escalations
description: "How structured decision logic turns ambiguous operational cases into consistent, auditable outcomes."
series: trust-safety
tags: [operations, trustandsafety, process, analytics]
image: "/images/malav-naik-convention-centre-dublin.jpg"
image_alt: "Malav Naik in a suit in front of a glass building under a blue sky"
week: 4
platforms: [blog, linkedin, medium]
canonical_url: "https://malavnaik.com/blog/decision-trees-for-escalations/"
linkedin_intro: "Two analysts looking at the same messy case should reach the same outcome. That's what a well-designed decision tree gives you: decisive questions first, facts before judgement, an owner for every outcome, an honest 'doesn't fit' branch, and versioning like code. Here's how I think about designing them."
status: "ready"
---

![Malav Naik in a suit in front of a glass building under a blue sky – Designing Decision Trees for Escalations: Classifying Messy Cases Consistently](/images/malav-naik-convention-centre-dublin.jpg){: width="1200" height="1599"}

Escalated cases rarely fit neatly into one box. One of the best tools for handling them consistently is decision-tree logic: a structured sequence of questions that routes each case to the right category and resolution path. It's the same idea as the business rules I wrote into data pipelines for years, applied to operations.

Here's how I think about designing those trees. Everything below is general practice, not tied to any specific company or platform's policies.

## Why not just use judgement?

Experienced analysts have good judgement. The problem is that judgement varies between people, shifts with fatigue, and is hard to audit. Two analysts looking at the same case should reach the same outcome. A decision tree makes the reasoning explicit and repeatable.

## Principle 1: Ask the most decisive question first

Order questions so the earliest ones split cases most cleanly. If one question sends 40% of cases straight to a known path, ask it first. This keeps trees short for common cases.

## Principle 2: Separate facts from judgements

Good trees distinguish questions with factual answers ("Is this account older than 30 days?") from questions that need interpretation ("Is this content intended to deceive?"). Put factual questions first; they're faster and more consistent. Leave interpretation for where it's genuinely needed.

## Principle 3: Every leaf needs an owner

Each end point should say what happens next and who does it. A leaf that says "escalate" without saying to whom just moves the ambiguity elsewhere.

## Principle 4: Build an explicit "doesn't fit" branch

When there are many categories, some cases will match none of them, or several. Rather than forcing a fit, route these to a review path and log them. That log becomes the evidence for adding or splitting categories.

## Principle 5: Version and measure the tree

Treat the tree like code:

- Version it, with a change log explaining why each change was made.
- Track how many cases reach each leaf. A leaf nobody reaches may be redundant; one that's overloaded may need splitting.
- Sample outcomes for consistency. If two analysts disagree often on one branch, the question there is unclear.

## Where AI fits

LLM-based tools can pre-classify cases and summarise context, which speeds up the first questions in a tree. But the tree still defines what "correct" means. AI makes the tree faster to apply; it doesn't replace the need to design it well.

Structured logic is unglamorous, but it's what makes operations at scale fair, fast and explainable.

*Views are my own and use public, general examples only.*
