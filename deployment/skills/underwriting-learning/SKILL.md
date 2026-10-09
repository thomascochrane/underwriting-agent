---
name: underwriting-learning
description: "Learn from deal outcomes, reporting and reviewer feedback."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, learning]
---

# Underwriting learning

Build a persistent, evidence-linked case history and use relevant prior experience to improve questions, risk assessments and explanations. This is retrieval and playbook learning; it does not retrain the underlying model or establish that predictive accuracy has improved.

## When to Use

- Start or revise underwriting and look for applicable prior lessons.
- Receive analyst corrections, investment decisions, weekly reporting, or realized outcomes.
- Ask which deals performed well, what was missed, or how underwriting should improve.

## Prerequisites

Load `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")` and this skill's `references/learning-records.md`. Use accessible retained evidence. If no history exists, initialize records as new events occur; never fabricate a track record.

## Procedure

1. Before a new review, retrieve relevant cases and lessons from `/workspace/underwriting-learning/`. Match asset class, originator/product, structure, economic period, vintage/seasoning and metric definitions. Note material differences and conflicting cases. Prior outcomes guide questions and scenarios; they are not evidence that the current borrower has the same facts.
2. Record a dated baseline from the original review: assumptions, forecasts, risk drivers, recommendation, confidence/limitations, and the separate human decision if known. Preserve the engine run and methodology version. Retrospective reconstruction must be labeled with its reconstruction date and sources; it is not a contemporaneous prediction.
3. Add events for reviewer feedback, reporting and outcomes, using the record contract. Feedback about presentation or a factual correction can improve future work immediately; a user's approval or rejection is a decision, not proof of subsequent credit performance. Keep unknown future outcomes unknown.
4. Define what 'quality' means for the comparison: realized loss/recovery, net cash yield, payment timing, liquidity stress, reporting reliability or another specified dimension. Record horizon and benchmark when supplied. Avoid an unsupported single good/bad label; a good investment outcome can coexist with weak documentation or an unsound original process.
5. Compare the thesis to observed results and identify candidate lessons with linked supporting and contradicting cases. Consider seasoning, incomplete outcomes, market effects and selection/survivorship bias. Unfunded deals have unknown investment outcomes absent independent evidence. Many reports from one originator do not establish broad generality or causation.
6. Maintain versioned lessons with evidence strength, scope, known exceptions and status. Apply supported lessons to future evidence requests, attention priorities and clearly labeled analytical hypotheses. Track which lessons were used and whether they helped. Do not automatically change credit cutoffs, engine calculations, mandatory evidence requirements or investment authority; propose those changes separately for a recorded human decision.
7. When asked to assess improvement, freeze a lesson version and assess it on later, unseen cases using only information available at each decision date. Specify metrics, sample, horizon and baseline. Report insufficient evidence when outcomes are immature or the sample is small; more saved memories alone do not prove better underwriting.

## Pitfalls

- Model memory is a compact index, not the authoritative deal database; do not store whole tapes or confidential narratives in global memory or skill source files.
- Do not turn an agent's own earlier inference into corroborating evidence by repeating it in a lesson.
- Later outcomes must not leak into reconstructed historical predictions.
- Retain disconfirming evidence and withdrawn lessons; do not rewrite history to make recommendations appear successful.

## Verification

Each event and lesson resolves to retained sources and dates, and corrections preserve prior versions. Repeated source uploads do not create extra evidence. Recommendations, decisions and observed outcomes are distinct. A new review identifies applied lessons and checks current-deal evidence. Report what history was actually saved; if persistence fails, disclose it rather than claiming to have learned.
