---
title: "Content moderation classifier, with a fairness check"
summary: "A toxicity classifier trained on 1.8 million public comments, with review-queue thresholds, a prevalence estimate and a fairness check by identity group – plus a demo that runs in your browser."
description: "A portfolio project by Malav Naik: a DistilBERT content moderation classifier on the public Civil Comments data, with threshold policies, a simulated review queue, prevalence estimation and false-positive rates by identity group."
order: 1
featured: true
code_url: https://github.com/malavnaik99/moderation-classifier
demo_url: https://huggingface.co/spaces/Malavnaik/moderation-classifier-demo
tech: [Python, scikit-learn, PyTorch, DistilBERT, Kaggle, Hugging Face, ONNX, transformers.js]
---
*Content warning: the training data is real toxic comments. Nothing on this page quotes them. This is a portfolio demo, not a production moderation system.*

## The problem
A moderation model gives every comment a score. The hard questions come after that: where do you draw the line, how much work lands on human reviewers, how much harmful content is really out there, and **is the model fair to everyone?** A single "accuracy" number answers none of these.

## What I built
Using the public [Civil Comments](https://www.kaggle.com/competitions/jigsaw-unintended-bias-in-toxicity-classification) data (1.8 million news-site comments, CC0 licence), I trained two models and measured them the way a trust & safety team would:

- a **simple baseline** (TF-IDF + logistic regression), and
- a **modern model** (DistilBERT, fine-tuned on Kaggle's free GPU).

For both I set two **threshold policies**, simulated a **review queue**, estimated **prevalence** from a small sample, and checked **false-positive rates by identity group**. Then I published the model with an honest model card and built a free demo.

## How it works

<svg viewBox="0 0 640 330" role="img" aria-labelledby="mc-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="14">
  <title id="mc-title">Flow: public comments are split into train, validation and test; two models are trained; thresholds are chosen on validation; the test set is used for the review queue, prevalence and fairness results; the model is published to Hugging Face and runs in the browser demo</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="170" y="10" width="300" height="44" rx="8"/>
    <rect x="40" y="90" width="260" height="44" rx="8"/><rect x="340" y="90" width="260" height="44" rx="8"/>
    <rect x="170" y="170" width="300" height="44" rx="8"/>
    <rect x="10" y="260" width="190" height="56" rx="8"/><rect x="225" y="260" width="190" height="56" rx="8"/><rect x="440" y="260" width="190" height="56" rx="8"/>
    <path d="M320 54v16M170 70h300M170 70v16M470 70v16M170 134v16M470 134v16M170 150h300M320 150v16M320 214v24M105 238h430M105 238v18M320 238v18M535 238v18"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="320" y="37">1.8M public comments (CC0)</text>
    <text x="170" y="117">Baseline: TF-IDF + logistic</text>
    <text x="470" y="117">DistilBERT (Kaggle free GPU)</text>
    <text x="320" y="197">Thresholds chosen on validation set</text>
    <text x="105" y="284">Review queue +</text><text x="105" y="302">prevalence</text>
    <text x="320" y="284">Fairness by</text><text x="320" y="302">identity group</text>
    <text x="535" y="284">Hugging Face model</text><text x="535" y="302">+ browser demo</text>
  </g>
</svg>

1. **Split the data** 80 / 10 / 10 into training, validation and test sets. Every number below comes from the 180,488 test comments, which neither model saw while training.
2. **Two threshold policies**, chosen on the validation set: *auto-action* only when the model is at least 90% precise, and *send to review* low enough to catch about 80% of toxic comments.
3. **Prevalence:** estimate the share of toxic comments from a random sample of 1,000, the way teams do it with human reviewers, and compare with counting the model's flags.
4. **Fairness:** for harmless comments that *mention* an identity group, measure how often each model wrongly flags them.
5. **Publish:** the notebook runs end to end on Kaggle; the model and its card are on Hugging Face; a compressed copy (67 MB) runs in the visitor's browser, so the demo costs nothing to host.

## Demo
Type a comment, move the threshold, and see the scores and what a review queue would do. The model runs in your browser: nothing you type is sent anywhere.

<p><button type="button" id="load-demo">Load the demo (downloads about 70 MB, once)</button> · <a href="https://huggingface.co/spaces/Malavnaik/moderation-classifier-demo">open it on Hugging Face</a></p>
<div id="demo-box"></div>
<script>
document.getElementById('load-demo').onclick = function () {
  this.disabled = true;
  document.getElementById('demo-box').innerHTML = '<iframe src="https://malavnaik-moderation-classifier-demo.static.hf.space" title="Moderation classifier demo" width="100%" height="760" style="border:1px solid var(--line);border-radius:8px" loading="lazy"></iframe>';
};
</script>

## Results
On 180,488 held-out test comments (8.0% toxic):

| | Simple baseline | DistilBERT |
|---|---|---|
| How well it ranks comments (ROC-AUC, 1 = perfect) | 0.941 | **0.957** |
| Toxic comments auto-actioned at ≥ 90% precision | 30.9% | **36.6%** |
| Comments sent to human review (to catch ~80% of toxic ones) | 10.7% | **8.5%** |
| Harmless comments wrongly flagged (identity-annotated set) | 12.8% | **9.6%** |

- **Prevalence:** a random sample of 1,000 comments estimates **7.4%** toxic (95% interval 5.9–9.2%), which contains the true 8.0%. Counting the modern model's review flags would say 11.7%, an overestimate.
- **Official score:** a late submission to the original Kaggle competition scored **0.915** on its bias-aware metric. The competition is closed, so this is a score only, with no ranking.
- **Browser version:** the compressed model made the same publish / review / auto-action decision as the full model on 97.2% of 2,000 test comments.

### Fairness: harmless comments wrongly flagged, by group mentioned

| Comment mentions | Simple baseline | DistilBERT |
|---|---|---|
| (all identity-annotated comments) | 12.8% | 9.6% |
| Black | 49.6% | 35.6% |
| white | 44.3% | 31.0% |
| gay or lesbian | 38.6% | 29.9% |
| Muslim | 37.2% | 25.8% |
| transgender | 31.6% | 24.5% |
| psychiatric or mental illness | 29.6% | 24.0% |
| Jewish | 23.8% | 16.0% |
| male | 20.9% | 14.6% |
| female | 19.7% | 14.0% |
| Asian | 14.2% | 8.8% |
| Christian | 12.4% | 8.2% |

The modern model is fairer for every group, but harmless comments mentioning some groups are still flagged up to about **4×** more often than average.

## What I learned
**What surprised me most:** harmless comments that simply *mention* a group get flagged far more often. With the simple model, half of the harmless comments mentioning "Black" were sent to review (50%), against 13% of harmless comments overall. The modern model shrank that gap, but it didn't close it. A single headline score (above 0.95 out of 1) hides this completely, so I would always break results down by group before trusting a moderation model.

**What I'd do next:** tackle that bias directly. I'd add more harmless training examples that mention these groups, track the false-positive rate for each group separately, and only call the model "better" when those gaps shrink.

## Links
- [Kaggle notebook](https://www.kaggle.com/code/malavnaik/moderation-classifier-civil-comments): the full analysis, top to bottom
- [Model and model card on Hugging Face](https://huggingface.co/Malavnaik/civil-comments-distilbert-moderation)
- [Demo on Hugging Face](https://huggingface.co/spaces/Malavnaik/moderation-classifier-demo)
- [Code on GitHub](https://github.com/malavnaik99/moderation-classifier)
