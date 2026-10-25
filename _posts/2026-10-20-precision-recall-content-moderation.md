---
id: 4
title: "Precision vs Recall in Content Moderation: The Trade-Off Every Integrity Team Faces"
slug: precision-recall-content-moderation
description: "Why no moderation system can catch everything without hurting innocent users, and how to choose where to set the line."
series: trust-safety
tags: [trustandsafety, machinelearning, metrics, ai]
image: "/images/malav-naik-convention-centre-dublin-suit.jpg"
image_alt: "Malav Naik in a suit outside a curved glass building"
week: 2
platforms: [blog, linkedin, medium]
canonical_url: "https://malavnaik.com/blog/precision-recall-content-moderation/"
status: ready
linkedin_intro: "Every content moderation system makes two kinds of mistakes: it removes things that were fine, and it misses things that weren't. You can't drive both to zero, so the real question is which mistake you'd rather make, for which harm. I wrote about how integrity teams choose where to set the line."
---

![Malav Naik in a suit outside a curved glass building – Precision vs Recall in Content Moderation: The Trade-Off Every Integrity Team Faces](/images/malav-naik-convention-centre-dublin-suit.jpg){: width="1200" height="1599"}

Every system that decides "is this content harmful?" makes two kinds of mistakes. It removes things that were fine, and it misses things that weren't. You can't drive both to zero. Choosing which mistake you'd rather make is one of the most important decisions an integrity team takes.

## The two numbers

- **Precision**: of everything the system flagged, how much was actually violating? Low precision means innocent users get actioned.
- **Recall**: of everything that was actually violating, how much did the system catch? Low recall means harm stays up.

Raise the threshold for flagging and precision goes up while recall goes down. Lower it and the reverse happens.

## Why the "right" threshold depends on the harm

There is no universal setting. It depends on the cost of each error:

| Harm type | Cost of a miss | Cost of a false positive | Usual bias |
|---|---|---|---|
| Child safety, imminent violence | Severe, possibly irreversible | User annoyance, appeal | Favour recall |
| Spam | Mild irritation | Lost legitimate post | Balanced |
| Satire, political speech | Low | Censorship concerns, trust loss | Favour precision |

## The human review layer changes the maths

Most teams don't rely on a single automated decision. A common pattern:

1. **High-confidence violations**: action automatically.
2. **Uncertain middle**: send to human reviewers.
3. **High-confidence benign**: leave alone.

Now the question becomes how wide to make the middle band. Wider means better decisions but more review cost and slower action. This is where the work becomes an operations problem as much as a modelling one.

## Measure on the right sample

Precision is easy to measure: sample what you flagged and check it. Recall is hard, because you need to find what you *didn't* flag. That requires sampling the unflagged population, which is usually huge and mostly benign. Teams that only measure precision tend to drift towards under-enforcement without noticing.

## Practical advice

- Report precision and recall per harm category, never as one blended number.
- Track appeal overturn rates as a real-world check on precision.
- Revisit thresholds when content patterns change. A threshold tuned last year may be wrong today.

In the next trust and safety post I'll look at prevalence: the metric that tries to answer "how much harm do users actually see?"

*Views are my own and use public, general examples only.*
