---
title: "SkillBot: from job title to the skills it needs"
summary: "My MSc project on personalised learning with large language models and knowledge graphs – plus a free, tested rebuild you can try in your browser: type a job title and see the skills real job ads ask for."
description: "A portfolio project by Malav Naik: SkillBot, an MSc research project combining an LLM and a knowledge graph for skill recommendations, and a free in-browser skills explorer built on public job-ad data with a leave-one-out evaluation."
order: 4
featured: true
code_url: https://github.com/malavnaik99/SkillBot-AI-Driven-Personalized-Learning-Platform
demo_url: https://huggingface.co/spaces/Malavnaik/skillbot-skills-explorer
tech: [Python, LLMs, Knowledge graphs, Prompt engineering, sentence-transformers, transformers.js, Hugging Face, GitHub Actions]
---
## The problem
People who want to change or grow their career keep asking the same question: **"what do I need to learn for this job?"** Course catalogues and job ads live in separate places, so the answer is usually guesswork.

## The MSc project
For my MSc in Data Analytics at the National College of Ireland, I designed and evaluated **SkillBot**, a chatbot that recommends skills and learning paths. As described in [my thesis](https://norma.ncirl.ie/9439/), it combined:

- a **GPT-3.5 model fine-tuned** on 15,000 skill-related conversations,
- a **knowledge graph** of about 2.3 million facts linking jobs, skills and courses (with TransE embeddings, stored in Neo4j), and
- **prompt templates** that feed the graph's context, the user's profile and the chat history into each answer.

**Reported in the thesis**, from a study with 50 participants: 87% recommendation accuracy, an F1-score of 84%, and a usability score (SUS) of 86/100.

*The code of that full system isn't public. The [GitHub repository](https://github.com/malavnaik99/SkillBot-AI-Driven-Personalized-Learning-Platform) holds the thesis, the data exploration and an early prototype notebook, so the numbers above can only be checked in the thesis itself.*

## The free rebuild: a skills explorer
The full system needed paid APIs and servers to run. So I rebuilt its core idea, **job title → skills**, as a small tool that runs in your browser for free, on public data, and tested it properly.

<svg viewBox="0 0 640 140" role="img" aria-labelledby="sb-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="14">
  <title id="sb-title">Flow: you type a job title; a small embedding model in the browser finds the 25 most similar real job ads; their skills plus the skills typical of their job area are counted; the top 10 skills are shown</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="10" y="40" width="140" height="60" rx="8"/><rect x="175" y="40" width="140" height="60" rx="8"/><rect x="340" y="40" width="140" height="60" rx="8"/><rect x="505" y="40" width="125" height="60" rx="8"/>
    <path d="M150 70h21M315 70h21M480 70h21"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="80" y="66">You type a</text><text x="80" y="84">job title</text>
    <text x="245" y="66">25 most similar</text><text x="245" y="84">real job ads</text>
    <text x="410" y="66">Count their skills</text><text x="410" y="84">+ their job area's</text>
    <text x="567" y="66">Top 10</text><text x="567" y="84">skills</text>
  </g>
</svg>

1. **Data:** 1,167 real job ads in five areas (IT, finance, sales, HR and business development), each with a list of skills. I kept only the job title, area and skills.
2. **Clean:** the skill lists were written by software and spelled inconsistently ("SQL", "sql"), so I merged the variants (5,774 → 4,984 distinct skills).
3. **Match by meaning:** a small open model (`all-MiniLM-L6-v2`) turns job titles into vectors, so "data wrangler" can still find data analyst ads.
4. **Suggest:** count the skills of the 25 most similar ads, plus the skills typical of their main job area, and show the top 10.

## Demo
Type a job title and see the skills most often asked for. Nothing you type is sent anywhere.

<p><button type="button" id="load-demo">Load the demo (downloads about 25 MB, once)</button> · <a href="https://huggingface.co/spaces/Malavnaik/skillbot-skills-explorer">open it on Hugging Face</a></p>
<div id="demo-box"></div>
<script>
document.getElementById('load-demo').onclick = function () {
  this.disabled = true;
  document.getElementById('demo-box').innerHTML = '<iframe src="https://malavnaik-skillbot-skills-explorer.static.hf.space" title="SkillBot skills explorer demo" width="100%" height="760" style="border:1px solid var(--line);border-radius:8px" loading="lazy"></iframe>';
};
</script>

## Results
To test it honestly, I hid each of the 1,167 ads in turn and asked the tool to suggest 10 skills from the ad's **title alone**, using only the other ads:

| Method | Suggested skills that were in the real ad |
|---|---|
| First version (before merging spellings) | 31% |
| Most common skills of the ad's area* | 47% |
| **Skills explorer** (similar ads + their area) | **48%** |

*This one cheats a little: it is told the job's area, which a title alone doesn't give you.

- About **5 of the 10 suggestions** are in the real ad, and the tool finds about **28%** of each ad's listed skills.
- The biggest gain came from cleaning the data, not from the model: merging spelling variants took it from 31% to 48%.
- I chose the final settings with this same test, so 48% is slightly optimistic.
- **Limits:** only five job areas (try "nurse" and it will struggle), and the skill lists were extracted by software, not people.

## Data and credits
[job-skill-set](https://huggingface.co/datasets/batuhanmtl/job-skill-set) by Batuhan Mutlu, built from [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) by Arsh Koneru, both under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Links
- [MSc thesis (NCI repository)](https://norma.ncirl.ie/9439/)
- [Skills explorer on Hugging Face](https://huggingface.co/spaces/Malavnaik/skillbot-skills-explorer)
- [Code on GitHub](https://github.com/malavnaik99/SkillBot-AI-Driven-Personalized-Learning-Platform) (the explorer is in `skills-explorer/`)
