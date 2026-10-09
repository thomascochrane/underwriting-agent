---
name: mca-tape-analysis
description: "Run MCA tape checks and interpret engine results."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, mca]
---

# MCA tape analysis

Operate the existing underwriting engine for MCA tapes and interpret its saved results. Preserve the engine's own AI mapper, AI review, validation gates, and deterministic calculations.

## When to Use

- Inspect or analyze an MCA tape, investigate a failed run, or interpret its workbook and run report.
- Do not apply this skill's MCA methodology to consumer lending or medical receivables.

## Prerequisites

The engine must be installed in the execution environment or exposed through a documented, configured service. The base Hermes deployment does not currently provide that connection. If absent, report "engine connection pending" and inventory inputs; do not claim a run.
The engine's Codex or Claude Code login is separate from Hermes authentication. Use the configured backend explicitly. Do not copy host credentials or install a substitute backend silently.
Read the installed engine's help and version/revision before using commands. Paths below are placeholders that must be replaced with verified paths and shell-quoted as data.

## How to Run

For a local engine installation, use `terminal` with the verified CLI:
- `underwrite --help`
- `underwrite --class mca inspect "<tape>"`
- `underwrite --class mca validate-config --config "<config>"`
- `underwrite --class mca run "<tape>" --config "<config>" --out "<new-run-output>" --ai-backend codex`
Only use these in the environment where the engine and its inputs exist. For a configured service, use its documented interface instead. Do not invent HTTP endpoints or run host Docker commands from Hermes.

Before creating outputs, load the shared record contract with `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Use its versioned review directory, source/evidence IDs, coverage states and issue dispositions. If running this skill alone, create the minimum records for this scope; do not imply the other topics were reviewed.

## Procedure

1. Confirm MCA classification, tape identity/hash, grain, originator, as-of date, sheet and methodology. Establish population: all originations, active-only, offered collateral or filtered sample; funding-date coverage; selection filters; and inclusion/exclusion of paid, charged-off, refinanced, sold or transferred advances. Reconcile counts/funded amounts to available broader control totals, stating their source and independence. If completeness is unverified, label supplied-population statistics and prohibit whole-book/lifetime conclusions. Never replace an unknown tape date with today's date.
2. Inspect columns/sheets and validate the selected configuration. Resolve output paths inside the chosen deal; use a unique run root to preserve prior runs.
3. Distinguish three options: `--channel percent|direct` records channel; `--deal <name>` selects an engine credit-methodology profile; `--profile internal|external` selects workbook presentation. None is a Hermes profile, and channel alone does not select a credit rule.
4. Use the requested applicable deal rule. If none is specified, report that the engine's house methodology will apply. Read resolved parameters from the run rather than hardcoding seasoning, payment thresholds, grace, or status rules in this skill.
5. Run the engine with its configured AI backend. Let its mapper propose unfamiliar columns/statuses and its gates accept or reject them. Do not duplicate the mapping/review loop in Hermes, bypass a gate, edit engine code, or change credit thresholds to achieve PASS.
6. Record command/options, engine revision, configuration identity, source hash/date, output paths, exit status, and run report in `run-summary.md`. Inspect the report even after exit 1: a failed validation can still produce useful artifacts.
7. Inspect verdict/reasons, warnings, tie-outs, mapping source, coverage, analytics failures, and `ai_review` details. Distinguish completed, skipped, and failed AI review. Cohort-level runs may intentionally skip AI review; loan-level runs can attempt review even on clean tapes to enrich questions.
8. Inspect accepted/rejected hypotheses and generated mapping drafts. Record drafts used or written. Mapping drafts may be reused automatically on later runs; preserve their identity. Draft deal-methodology configs are different and are not activated by this skill.
9. Read each run's Definitions and Method alongside analytical tables. Identify denominator, cohort age, payment frequency, gross/participated basis and default definition. Explicitly distinguish snapshot-inferred default timing and current outstanding default stock from observed historical default events, ever-default incidence and realized net loss. Do not infer cures, transitions, recovery timing or post-default recoveries without the necessary event/payment history. The current engine's reconstructed curves are not a complete lifetime event history.
10. Present cash collections and noncash renewal credits separately. Verify whether reported MOIC includes renewal credits applied to RTR; if so label it accordingly, never cash-only realization. Label the current engine's annualized yields as simple contractual annualizations, not realized cash IRR or loss-adjusted profitability. Net of commission excludes neither all costs nor losses; identify remaining funding, servicing and other costs. Cash IRR requires dated actual cash flows and a validated calculation.
11. Return workbook/report links, population statement, metric definitions, findings and questions. Record evidence version, coverage and issue dispositions in the review records. Keep document review separate from the engine result. Do not infer this instrument's borrowing-base coverage or repayment capacity solely from portfolio analytics; those require transaction-specific analysis.

## Pitfalls

- `--no-ai` disables AI mapping and review. Use only when requested or explicitly agreed as a limited diagnostic run, and label the result accordingly. Unknown layouts may then fail.
- Model output cannot certify source accuracy. Passing arithmetic gates can still leave semantic questions.
- Engine login failure must not be hidden by presenting deterministic results as AI-reviewed.
- Vintage summaries cannot support borrower-level concentration or reconstructed loan-level default curves.
- Workbook generation does not prove Excel formulas were recalculated. Report Python calculations and actual spreadsheet recalculation checks separately.
- Engine PASS is a data/methodology validation verdict, not investment approval.

## Verification

Verify outputs match this input, source version, date, population and methodology. Summarize failures, warnings, absent analytics and actual AI status. Check each performance claim for population scope, inferred versus observed timing, default stock versus lifetime loss, cash versus renewal credits, and contractual versus realized returns. No favorable historical/return claim may exceed the available evidence.