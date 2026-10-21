---
title: "Ask the EU Digital Services Act"
summary: "Type a question in plain English and get the articles of the EU Digital Services Act that answer it, quoted and linked – a search demo that runs in your browser, tested on 25 questions."
description: "A portfolio project by Malav Naik: semantic search over the EU Digital Services Act (Regulation (EU) 2022/2065), with keyword, semantic and hybrid search compared on 25 hand-written test questions."
order: 3
featured: true
code_url: https://github.com/malavnaik99/eu-dsa-search
demo_url: https://huggingface.co/spaces/Malavnaik/ask-the-dsa
tech: [Python, BeautifulSoup, sentence-transformers, BM25, transformers.js, Kaggle, Hugging Face, GitHub Actions]
---
*Not legal advice. This demo only quotes the law and links to it; it never writes answers of its own.*

## The problem
The EU's Digital Services Act (DSA) sets the rules for how online platforms handle illegal content, appeals, ads and transparency. It is 93 articles and 156 recitals long. People who work in trust & safety need to find **the right article** fast, but they ask in everyday words ("can a platform take down my post without telling me why?"), while the law uses its own terms ("statement of reasons").

## What I built
A search tool that takes a plain-English question and returns the three articles most likely to answer it, each with the matching paragraph quoted and a link to the official text.

I deliberately made it **quote the law only**: no AI-written answer. A generated answer can sound confident and still be wrong about the law, while a quoted paragraph can always be checked. This also means it runs free in the visitor's browser.

## How it works

<svg viewBox="0 0 640 250" role="img" aria-labelledby="dsa-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="14">
  <title id="dsa-title">Flow: the official DSA text from EUR-Lex is split into 638 paragraph chunks and published as a Hugging Face dataset; each chunk is turned into a vector by a small embedding model; in the browser the question is turned into a vector with the same model and the closest articles are shown with quotes and links; three search methods are compared on 25 test questions in a Kaggle notebook</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="10" y="10" width="190" height="56" rx="8"/><rect x="225" y="10" width="190" height="56" rx="8"/><rect x="440" y="10" width="190" height="56" rx="8"/>
    <rect x="120" y="160" width="190" height="56" rx="8"/><rect x="335" y="160" width="190" height="56" rx="8"/>
    <path d="M200 38h21M415 38h21M320 66v40M215 106h215M215 106v50M430 106v50"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="105" y="34">Official DSA text</text><text x="105" y="52">(EUR-Lex)</text>
    <text x="320" y="34">638 paragraph chunks</text><text x="320" y="52">(Hugging Face dataset)</text>
    <text x="535" y="34">Vectors from a small</text><text x="535" y="52">embedding model</text>
    <text x="215" y="184">Kaggle: 3 search</text><text x="215" y="202">methods, 25 questions</text>
    <text x="430" y="184">Browser demo: top 3</text><text x="430" y="202">articles, quoted</text>
  </g>
</svg>

1. **Get the official text.** The English DSA from EUR-Lex, the EU's official law website.
2. **Split it into chunks**, one per paragraph of each article (long lists, like the definitions in Article 3, are split into their points), plus the recitals. Each chunk keeps its article number, title, chapter and link: 638 chunks in total, published as an [open dataset](https://huggingface.co/datasets/Malavnaik/eu-dsa-articles).
3. **Write a test set first:** 25 questions in everyday language, each with the article(s) that answer it, checked against the text.
4. **Compare three ways of searching:** classic **keyword search** (BM25), **semantic search** with the small open model `all-MiniLM-L6-v2` (it matches meaning, not exact words), and a **hybrid** of the two.
5. **Ship the winner** in a demo that runs entirely in your browser, using a compressed copy of the same model (about 23 MB).

## Demo
Ask a question and see the top 3 articles. Nothing you type is sent anywhere.

<p><button type="button" id="load-demo">Load the demo (downloads about 25 MB, once)</button> · <a href="https://huggingface.co/spaces/Malavnaik/ask-the-dsa">open it on Hugging Face</a></p>
<div id="demo-box"></div>
<script>
document.getElementById('load-demo').onclick = function () {
  this.disabled = true;
  document.getElementById('demo-box').innerHTML = '<iframe src="https://malavnaik-ask-the-dsa.static.hf.space" title="Ask the EU Digital Services Act demo" width="100%" height="760" style="border:1px solid var(--line);border-radius:8px" loading="lazy"></iframe>';
};
</script>

## Results
How often the right article was found, on the 25 test questions (searching the 482 article chunks). Keyword = BM25:

| | Keyword | Semantic | Hybrid |
|---|---|---|---|
| Ranked first | 48% | 52% | **56%** |
| In top 3 | 68% | **84%** | 80% |
| In top 5 | 72% | **92%** | 84% |
| MRR* | 0.599 | 0.675 | **0.701** |

*Mean reciprocal rank: 1 means the right article always came first.

- **Why semantic search in the demo:** the demo shows three articles, and semantic search put the right one in the top 3 most often (84%). The hybrid was slightly better at ranking it *first*.
- **The browser version is weaker:** the compressed model in the demo finds the right article in the top 3 for **72%** of the questions (56% first, 92% in the top 5). That's the honest price of a free, private demo, and the reason it always shows three results with links.
- **Where it fails:** everyday words that the law expresses differently. "Does a platform have to explain why it removed my post?" should find Article 17, which the law calls a *statement of reasons* and which never uses the word "explain". The hybrid search ranked three other articles above it.

## Links
- [Kaggle notebook](https://www.kaggle.com/code/malavnaik/searching-the-eu-digital-services-act): the evaluation, top to bottom
- [Dataset on Hugging Face](https://huggingface.co/datasets/Malavnaik/eu-dsa-articles)
- [Demo on Hugging Face](https://huggingface.co/spaces/Malavnaik/ask-the-dsa)
- [Code on GitHub](https://github.com/malavnaik99/eu-dsa-search)

*Source of the law: [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng), © European Union. Only the Official Journal text is authentic.*
