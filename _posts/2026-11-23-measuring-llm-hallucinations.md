---
id: 13
title: "Measuring LLM Hallucinations: A Simple Evaluation Harness You Can Build in an Afternoon"
seo_title: "Measuring LLM Hallucinations: A Simple Harness"
slug: measuring-llm-hallucinations
description: "A minimal Python harness for checking whether an LLM's answers are supported by the context you gave it."
series: genai
tags: [llm, evaluation, python, ai]
image: "/images/malav-naik-thames-tower-bridge.jpg"
image_alt: "Malav Naik sitting on a wall by the Thames with Tower Bridge behind"
week: 7
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/measuring-llm-hallucinations/"
status: "ready"
linkedin_intro: "You don't need a big evaluation platform to start measuring hallucinations. A CSV of test questions and a short Python script that asks a judge model whether each claim is supported by the retrieved context will teach you more than a week of manual testing. Here's the harness, plus three rules that make it useful: freeze the test set, spot-check the judge, and read every failure."
---

![Malav Naik sitting on a wall by the Thames with Tower Bridge behind – Measuring LLM Hallucinations: A Simple Evaluation Harness You Can Build in an Afternoon](/images/malav-naik-thames-tower-bridge.jpg){: width="1200" height="1600"}

You don't need a big evaluation platform to start measuring hallucinations. A spreadsheet of test questions and fifty lines of Python will teach you more about your system than a week of manual testing.

## The idea

For a retrieval-based system, a "hallucination" is a claim in the answer that isn't supported by the retrieved context. So the harness checks three things for each test case:

1. What context was retrieved?
2. What did the model answer?
3. Is each claim in the answer supported by the context?

## The test file

Start with a CSV:

```csv
id,question
1,"What skills does a data engineer need?"
2,"Which cloud services support PaaS SQL?"
```

## The harness

```python
import csv, json

def run_case(question, retrieve, generate):
    context = retrieve(question)
    answer = generate(question, context)
    return {"question": question, "context": context, "answer": answer}

def judge(answer, context, judge_llm):
    prompt = (
        "List each factual claim in the ANSWER. For each, say SUPPORTED if the "
        "CONTEXT states it, otherwise UNSUPPORTED. Reply as JSON: "
        '[{"claim": "...", "verdict": "SUPPORTED"}]\n\n'
        f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"
    )
    return json.loads(judge_llm(prompt))

def evaluate(path, retrieve, generate, judge_llm):
    supported = unsupported = 0
    with open(path) as f:
        for row in csv.DictReader(f):
            result = run_case(row["question"], retrieve, generate)
            for c in judge(result["answer"], result["context"], judge_llm):
                if c["verdict"] == "SUPPORTED":
                    supported += 1
                else:
                    unsupported += 1
                    print("UNSUPPORTED:", row["id"], c["claim"])
    total = supported + unsupported
    print(f"Supported claims: {supported}/{total} = {supported / total:.1%}")
```

Plug in your own `retrieve`, `generate` and `judge_llm` functions.

## Three rules that make it useful

**Freeze the test set.** Don't edit questions to make scores go up.

**Spot-check the judge.** Using an LLM as a judge is fast, but it makes mistakes too. Hand-label 30–50 claims and compare. If the judge disagrees with you often, fix the judge prompt before trusting any scores.

**Read every failure.** The printed unsupported claims are the most valuable output. Group them: retrieval missed the fact, the model invented something, or the data itself was wrong. Each group has a different fix.

## Going further

Once this works, add it to CI so every prompt or retrieval change runs the evaluation. Track the score over time. Open-source frameworks such as Ragas and OpenAI's Evals offer more sophisticated metrics, but a simple harness you understand fully is the best place to start.
