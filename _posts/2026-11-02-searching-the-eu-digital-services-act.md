---
id: 52
title: "I Built a Search Tool for the EU Digital Services Act, and Tested It First"
slug: searching-the-eu-digital-services-act
description: "How I turned the EU Digital Services Act into a free, in-browser search tool that quotes and links the law, and how I measured keyword, semantic and hybrid search on 25 test questions."
series: trust-safety
tags: [trustandsafety, rag, nlp, eu]
image: "/images/malav-naik-grand-canal-square-dublin.jpg"
image_alt: "Malav Naik in a square with modern buildings in Dublin"
week: 26
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/searching-the-eu-digital-services-act/"
linkedin_intro: "The EU Digital Services Act is 93 articles long, and people ask about it in everyday words the law doesn't use. So I built a small search tool that finds the right articles and quotes them, with no AI-written answers, running free in the browser. Before shipping it, I wrote 25 test questions and compared keyword, semantic and hybrid search. Here's what worked, and where it still fails."
x_post: "The EU Digital Services Act is 93 articles long. I built a free search tool that finds and quotes the right articles from a plain-English question, and tested 3 search methods on 25 questions first. Not legal advice."
status: ready
---

![Malav Naik in a square with modern buildings in Dublin – I Built a Search Tool for the EU Digital Services Act, and Tested It First](/images/malav-naik-grand-canal-square-dublin.jpg){: width="1200" height="1599"}

The EU's Digital Services Act (DSA) sets the rules for how online platforms handle illegal content, appeals, ads and transparency. If you work in trust & safety, you keep needing to find *the* article that covers a situation. But you think in everyday words ("can they remove my post without saying why?"), and the law uses its own ("statement of reasons").

So I built a small search tool: type a question, get the three articles most likely to answer it, each with the matching paragraph quoted and a link to the official text. You can [try it on the project page](https://malavnaik.com/projects/ask-the-dsa/). It runs in your browser, so nothing you type is sent anywhere.

*Not legal advice. The tool only quotes the law.*

## Why it quotes the law instead of answering

The popular approach is "RAG": find the relevant text, then have an AI model write an answer from it. For law, I chose to stop at the first half. A generated answer can sound confident and still get the law wrong; a quoted paragraph with a link can always be checked. It also meant the whole thing could run for free, with no model server to pay for.

## 1. Split the law into searchable pieces

I took the official English text from EUR-Lex (the EU's law website, whose documents may be reused with credit) and split it into one chunk per paragraph of each article. Long lists, like the definitions in Article 3, are split into their points. Each chunk keeps its article number, title, chapter and link. That gave 638 chunks (93 articles plus 156 recitals), which I published as an [open dataset on Hugging Face](https://huggingface.co/datasets/Malavnaik/eu-dsa-articles).

## 2. Write the test before choosing the method

Before building the demo, I wrote **25 questions in everyday language**, each with the article(s) that answer it, checked against the text. Then I compared three ways of searching:

- **Keyword search (BM25):** the classic approach, matching words.
- **Semantic search:** a small open model (`all-MiniLM-L6-v2`) turns text into vectors, so it can match meaning, not just exact words.
- **Hybrid:** both rankings combined.

| Measure | Keyword | Semantic | Hybrid |
|---|---|---|---|
| Right article ranked first | 48% | 52% | **56%** |
| Right article in the top 3 | 68% | **84%** | 80% |
| Right article in the top 5 | 72% | **92%** | 84% |

The demo shows three articles, so I shipped semantic search: it had the right article in the top 3 most often. The full evaluation is in a [Kaggle notebook](https://www.kaggle.com/code/malavnaik/searching-the-eu-digital-services-act).

## 3. Run it in the browser

The demo uses a compressed copy of the same model (about 23 MB), downloaded once by the visitor's browser, plus the pre-computed vectors for every chunk. I re-ran the 25 questions with the compressed model, and it is weaker: the right article was in the top 3 for **72%** of questions (56% first, 92% in the top 5). That's the honest cost of a free, private demo, and why it always shows three results with links rather than one "answer".

## Where it fails

The misses are telling. "Does a platform have to explain why it removed my post?" should find Article 17, but the law calls this a *statement of reasons* and never uses the word "explain". The everyday question and the legal wording barely overlap, and a small model doesn't always bridge the gap.

## What I'd do next

- **Write more test questions**, ideally with people who work with the DSA, because 25 questions is a small test.
- **Try a stronger embedding model** and see whether the gains survive compression for the browser.

## What it costs

€0: a free static Hugging Face Space, a free dataset, and GitHub Actions and Kaggle on their free tiers. The [code is on GitHub](https://github.com/malavnaik99/eu-dsa-search).

*Source of the law: EUR-Lex, © European Union. Only the Official Journal text is authentic.*
