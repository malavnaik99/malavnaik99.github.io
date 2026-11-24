---
id: 12
title: "Prevalence: The Integrity Metric That Asks How Much Harm Users Actually See"
seo_title: "Prevalence, the Integrity Metric, Explained"
slug: prevalence-metric-trust-safety
description: "Why counting removals can mislead, and how prevalence measurement gives a more honest picture of platform safety."
series: trust-safety
tags: [trustandsafety, metrics, statistics, datascience]
image: "/images/malav-naik-red-shirt-green-hedge.jpg"
image_alt: "Malav Naik in a red shirt in front of a green hedge"
week: 6
platforms: [blog, linkedin, medium]
canonical_url: "https://malavnaik.com/blog/prevalence-metric-trust-safety/"
status: "ready"
linkedin_intro: "\"We removed 10 million violating posts this quarter\" sounds like good news, but it could mean better enforcement, more harm, or a more aggressive classifier. That's why many integrity teams track prevalence: the share of views that violate policy, estimated by sampling. Here's how it works, why it beats counting removals, and why it's really a data science problem."
---

![Malav Naik in a red shirt in front of a green hedge – Prevalence: The Integrity Metric That Asks How Much Harm Users Actually See](/images/malav-naik-red-shirt-green-hedge.jpg){: width="960" height="1280"}

If a platform says "we removed 10 million violating posts this quarter," is that good news? It might mean enforcement improved. It might mean there was more harmful content. It might mean the classifier became more aggressive. The number alone can't tell you.

That's why many integrity teams track **prevalence**.

## What prevalence measures

Prevalence estimates the share of what users see that violates a policy. Typically it's based on views, not posts:

> Prevalence = estimated violating views ÷ total views

A post seen by one person and a post seen by a million people aren't equal harms. Weighting by views measures exposure, which is closer to what users experience.

## How it's estimated

You can't review every view. So prevalence is estimated by sampling:

1. Randomly sample content views across the platform (weighted so popular content appears in proportion to how often it's seen).
2. Have trained reviewers label each sampled item against policy.
3. Compute the violating share and a confidence interval.

Because violations are usually rare, samples need to be large to give a useful interval. Estimating something that occurs in 0.05% of views with good precision needs many thousands of labelled samples.

## Why it beats counting removals

| Metric | What it tells you | Weakness |
|---|---|---|
| Items removed | Enforcement activity | Rises with both more harm and better detection |
| Proactive rate | Share caught before users report | Says nothing about what's missed |
| Prevalence | Harm users actually saw | Expensive; needs careful sampling |

Removal counts measure effort. Prevalence measures outcome.

## The hard parts

- **Labelling consistency.** If reviewers disagree, prevalence is noisy. Measuring inter-rater agreement is essential.
- **Rare harms.** For very rare categories, confidence intervals can be wider than the estimate itself.
- **Policy changes.** If the definition changes, the trend line breaks. Document changes alongside the metric.

## Why data people should care

Prevalence is a sampling and estimation problem as much as a policy one. Stratified sampling, confidence intervals and annotation quality are all core data science skills. It's one of the clearest examples of data work directly shaping how safe a platform is.

*Views are my own and use public, general examples only.*
