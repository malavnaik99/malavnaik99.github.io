---
id: 43
title: "What 1.8 Million Comments Taught Me About Fair Content Moderation"
slug: trust-safety-dashboard-public-data
description: "I trained two content moderation models on 1.8 million public comments and measured them like a trust & safety team: thresholds, review queues, prevalence and fairness."
series: trust-safety
tags: [trustandsafety, datascience, portfolio, python]
image: "/images/malav-naik-grand-canal-square-dublin.jpg"
image_alt: "Malav Naik in a square with red poles and modern buildings"
week: 22
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/trust-safety-dashboard-public-data/"
linkedin_intro: "I trained two content moderation models on 1.8 million public comments and checked them the way a trust & safety team would. The modern model was better on every measure, but harmless comments that simply mention some groups were still flagged up to about four times more often than average. Here is what I built, what I found, and a demo you can try in your browser."
x_post: "I trained two content moderation models on 1.8M public comments and checked them like a trust & safety team would: review queues, prevalence and fairness by identity group. The fairness results surprised me."
status: ready
---

![Malav Naik in a square with red poles and modern buildings – What 1.8 Million Comments Taught Me About Fair Content Moderation](/images/malav-naik-grand-canal-square-dublin.jpg){: width="1200" height="1599"}

*Content warning: this project uses a dataset of real toxic comments. This post doesn't quote any of them.*

You can't share real moderation data from work, and you shouldn't. But you can practise every core trust and safety analytics skill on public data. So I did: I trained two content moderation models on 1.8 million public comments and measured them the way a trust and safety team would.

Everything is public: the [Kaggle notebook](https://www.kaggle.com/code/malavnaik/moderation-classifier-civil-comments), the [model and its model card](https://huggingface.co/Malavnaik/civil-comments-distilbert-moderation), a [demo that runs in your browser](https://huggingface.co/spaces/Malavnaik/moderation-classifier-demo) and the [code](https://github.com/malavnaik99/moderation-classifier). The project write-up is [on my site](https://malavnaik.com/projects/moderation-classifier/).

## The data

The [Civil Comments](https://www.kaggle.com/competitions/jigsaw-unintended-bias-in-toxicity-classification) dataset has 1.8 million comments from news sites, each rated by several people for toxicity, insults, threats and more. It's released under CC0, so anyone can use it. Crucially, a subset is also labelled with the identity groups each comment *mentions*, which makes a fairness check possible. 8% of comments are toxic.

## Two models

- **A simple baseline:** TF-IDF word features with logistic regression. Fast, cheap and surprisingly strong.
- **A modern model:** DistilBERT, a small transformer that reads words in context, fine-tuned on Kaggle's free GPU.

Every number below comes from 180,488 test comments that neither model saw during training.

| | Simple baseline | DistilBERT |
|---|---|---|
| Ranking quality (ROC-AUC, 1 = perfect) | 0.941 | **0.957** |
| Toxic comments auto-actioned at ≥ 90% precision | 30.9% | **36.6%** |
| Comments sent to human review (to catch ~80% of toxic ones) | 10.7% | **8.5%** |

## Thresholds are policy, not maths

A model only gives scores. Someone has to decide where the lines go. I used two:

- **Auto-action** only where the model is at least 90% precise, because wrongly removing a comment is costly.
- **Send to review** low enough to catch about 80% of toxic comments, with humans checking everything in between.

With the modern model, that means about 3% of comments are actioned automatically and 8.5% go to reviewers. That's about 20% less review work than the baseline for the same coverage.

## Don't count the model's flags

How much toxic content is there? Counting the model's flags would say 11.7%. A random sample of 1,000 comments, the way you'd do it with human reviewers, estimates **7.4%** (95% interval 5.9–9.2%), and the true figure is 8.0%. The small sample wins.

## The fairness check

Here's the finding that matters most. Among **harmless** comments that simply mention a group, how many get wrongly flagged?

| Comment mentions | Simple baseline | DistilBERT |
|---|---|---|
| (average, identity-annotated comments) | 12.8% | 9.6% |
| Black | 49.6% | 35.6% |
| white | 44.3% | 31.0% |
| gay or lesbian | 38.6% | 29.9% |
| Muslim | 37.2% | 25.8% |
| transgender | 31.6% | 24.5% |

The modern model is fairer for every group, but harmless comments mentioning some groups are still flagged up to about four times more often than average. The model has partly learned that *naming* a group is a sign of toxicity.

## What I learned

**What surprised me most:** harmless comments that simply *mention* a group get flagged far more often. With the simple model, half of the harmless comments mentioning "Black" were sent to review (50%), against 13% of harmless comments overall. The modern model shrank that gap, but it didn't close it. A single headline score (above 0.95 out of 1) hides this completely, so I would always break results down by group before trusting a moderation model.

**What I'd do next:** tackle that bias directly. I'd add more harmless training examples that mention these groups, track the false-positive rate for each group separately, and only call the model "better" when those gaps shrink.

## Try it

The [demo](https://huggingface.co/spaces/Malavnaik/moderation-classifier-demo) runs a compressed copy of the model in your browser, so nothing you type leaves your device. Move the threshold and watch decisions change. It's a portfolio demo, not a production moderation system.

For the record, a late submission to the original Kaggle competition scored 0.915 on its bias-aware metric. The competition closed years ago, so that's a score only, with no ranking.
