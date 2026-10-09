---
name: portfolio-performance-review
description: "Review weekly reporting against underwriting assumptions."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, monitoring, learning]
---

# Portfolio performance review

Compare received reporting with the original credit thesis and prior comparable periods. Preserve the difference between management reporting, reproduced calculations, and independently corroborated cash performance.

## When to Use

- Weekly or monthly servicing reports, updated tapes, covenant certificates, collections reports, or revised forecasts arrive.
- The user asks what changed, whether a deal is performing as expected, or which original concerns have materialized.

## Prerequisites

Identify the deal, legal entity, facility, asset class, reporting period and as-of date. Locate the original dated underwriting and any prior reports actually available. Missing baselines allow a current-period review only.

Load `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Keep each reporting review in a new review directory with source versions, evidence, coverage, and issues. Receiving a report is the trigger; this skill does not schedule jobs or connect a reporting feed.

## Procedure

1. Inventory the reporting package and gaps. Preserve source bytes and distinguish report period, receipt time, and review time. Treat revised reports as new versions, retaining the superseded versions. A duplicated report is not another observation.
2. Match populations before comparing: stable account IDs, originator, product, vintage, seasoning, facility participation and eligibility basis. Explain changes caused by purchases, sales, renewals, payoffs, charge-offs, substitutions or changed definitions. If reconciliation is unavailable, mark comparability limited.
3. Create a metric bridge with prior comparable actual, original forecast for the same period, current actual, variance, definition, denominator, and evidence. Use reproducible calculations and the tested engine when available. Do not infer cash collections from balance reductions alone.
4. For MCA, separate actual cash receipts from renewal/refinance credits, modifications, reversals, repurchases, recoveries and write-offs. Compare vintage performance at equivalent seasoning; show volume and concentration changes separately from changes in credit quality. Follow `mca-tape-analysis` when an updated tape requires the engine.
5. Review applicable collections, delinquencies, defaults/losses, recoveries, collateral coverage, concentrations, liquidity and covenant headroom. Use the actual contract and amendments effective for that reporting period. Record unavailable tests as unperformed; missing or late reporting is not proof of good performance or by itself proof of default.
6. Write `performance-review.md` and `performance-metrics.csv` with the bridge, tested assumptions, changes in issues, questions and next evidence needed. Separate an early warning, a reported breach and a verified breach. Do not invent universal thresholds or silently revise the original forecast to match actuals.
7. Use `underwriting-learning` to record supported observations about the original thesis, with the original review and this reporting review linked. A partial weekly report can update an observation; it cannot establish final deal success or loss. Send requested findings and files through the current authorized chat; lender communications remain drafts unless requested.

## Pitfalls

- Successive weekly snapshots are overlapping observations, not independent deals; cumulative totals must not be summed across weeks.
- Growth can dilute delinquency ratios while older cohorts deteriorate.
- Contractual yield, merchant collections, originator profitability and cash returned to Zivoe describe different outcomes.
- Forecast assumptions and contemporaneous credit judgments must remain recoverable after later information arrives.

## Verification

Comparisons use aligned dates, populations, units and definitions or disclose the mismatch. Every material variance has reproducible support or a stated limitation. Reporting gaps and unresolved issues remain visible. Lessons cite the exact reporting versions; no recurring job, credit-policy change, or external lender message is implied.
