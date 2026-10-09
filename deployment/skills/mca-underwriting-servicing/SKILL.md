---
name: mca-underwriting-servicing
description: "Review MCA origination, renewals and collections."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, mca]
---

# MCA underwriting and servicing review

Review an MCA originator's policies and operating evidence alongside available tape findings. Distinguish stated policy from observed practice and preserve open questions.

## When to Use

- Review MCA underwriting, broker channels, renewals, stacking, collections, workouts, or servicing arrangements.
- Do not use for non-MCA asset classes or to change engine credit rules.

## Prerequisites

Available underwriting/collections policies, sample agreements or process descriptions, and optionally an MCA engine run. Missing documents or identifiers limit the conclusions. Use `read_file` and the installed document skills for extraction, and the MCA tape skill for calculations.

Before creating outputs, load the shared record contract with `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Use its versioned review directory, source/evidence IDs, coverage states and issue dispositions. If running this skill alone, create the minimum records for this scope; do not imply the other topics were reviewed.

## Procedure

1. Identify product and origination channels: direct/broker, purchased receivables, funding positions, merchant eligibility, verification, approval exceptions, and delegated authority. Cite policy version and date.
2. Extract how merchant revenue/obligations are verified, payment capacity assessed, fraud screened, stacking identified and exceptions approved. For implementation evidence record sample population, selection method, sample count, period, exceptions and exception rate when calculable. Label management-selected samples and selection bias. A few compliant files do not demonstrate universal policy adherence.
3. Examine renewals and refinancings. Distinguish new merchant cash, payoff/renewal credits, original funding, and commissions. Ask whether old exposures close through actual cash collection or refinancing; avoid counting renewal credit as independent cash recovery.
4. Review payment frequency, ACH failures, reduced payments, rewritten schedules, settlement discounts, legal collections, charge-offs, and recovery practices. Distinguish operational status words from the engine's derived delinquency and default tests.
5. Compare applicable policies with existing engine findings: modified terms, stale payment records, concentration, repeated advances, vintage behavior, and exceptions. Cite the exact run and table. Lack of a tape field means a policy could not be tested, not that the policy was followed.
6. Assess servicing dependencies, bank/account control evidence, reconciliations, continuity, and backup servicing arrangements. Distinguish a plan on paper from a tested or contracted capability.
7. Produce `mca-operations-review.md` with policy-to-evidence comparisons, sample scope, exceptions, limitations, coverage and issue dispositions. Feed cited questions into the consolidated register without sending them. Link observations to the retained evidence version and exact tape run.

## Pitfalls

- "Active" or a rewritten payoff schedule does not establish that payments are current.
- Fast growth and frequent renewals can obscure seasoning and cash realization.
- Merchant concentration requires stable merchant identifiers across advances; advance IDs alone are insufficient.
- A policy's legal characterization is not an enforceability conclusion.
- Never use another originator's conventions as facts for this lender.

## Verification

Every practice is labeled stated, observed, contradicted, or unverified. Observed claims specify sample scope and selection limitations. Tape comparisons use correct definitions, dates and population. Material gaps have issue dispositions; no underwriting rule or source file was altered.