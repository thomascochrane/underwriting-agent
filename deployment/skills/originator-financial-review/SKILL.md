---
name: originator-financial-review
description: "Review originator earnings, liquidity and debt."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, diligence]
---

# Originator financial review

Assess an originator's financial condition from supplied financial statements and supporting schedules. Keep the originator's corporate finances separate from the collateral portfolio and the investment instrument.

## When to Use

- Review financial statements, management accounts, funding costs, or liquidity.
- Do not use to perform loan-level tape calculations or provide an audit opinion.

## Prerequisites

Accessible statements and their entity, currency, accounting basis, and periods. Use installed PDF/Excel skills for extraction and calculation. Incomplete statements support a limited review, not a completed financial assessment.

Before creating outputs, load the shared record contract with `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Use its versioned review directory, source/evidence IDs, coverage states and issue dispositions. If running this skill alone, create the minimum records for this scope; do not imply the other topics were reviewed.

## Procedure

1. Build a period/entity coverage table. Distinguish parent, operating company, borrower SPV, and consolidated group. Separate audited, reviewed, and management-prepared figures.
2. Assemble revenue, earnings, cash, receivables, debt, equity, and available cash-flow information with citations. Preserve missing or excluded expenses; do not equate blank expenses with zero.
3. Reconcile overlapping periods before building LTM figures. Do not add YTD to an overlapping annual period. Record fiscal/calendar differences and restatements.
4. Build a sourced bridge from reported earnings to recurring earnings and then cash generation. Separate applicable noncash provisions, realized losses, funding costs, commissions, receivables growth, intercompany flows, distributions and other adjustments; avoid counting the same cash outflow twice. Reconcile to available cash-flow statements and cash balances. Mark unsupported adjustments and unavailable bridges untested. Calculate trends and ratios reproducibly with numerator, denominator, period and currency; inferred debt from interest expense is not disclosed debt.
5. Build a dated debt-service/funding schedule: borrower, lender, balance, rate basis, interest/principal obligations, maturity, security, covenant definitions and evidence. Reconcile to the balance sheet. Calculate applicable covenant headroom on aligned dates using the actual contractual definitions and explain the breach direction. If the definition or inputs are missing, mark the test unperformed rather than compliant.
6. Compare dated obligations and planned advance funding with unrestricted cash and demonstrably drawable facilities at the correct entity. Separate nominal commitments from availability after borrowing-base limits, covenants and conditions. Assess a supported funding-interruption or slower-collections case with dated assumptions; identify the cash gap and timing. A scenario is not a forecast. Where inputs or a suitable calculation tool are absent, mark testing unperformed and avoid a favorable liquidity conclusion.
7. Write `financial-review.md` with the cash bridge, debt schedule, covenant/liquidity headroom, scenario assumptions and results, limitations and issues. Keep originator survival and borrowing-SPV repayment separate. Use tested calculation tools; simple reconciliations must be reproducible and checked, and complex new models require separate implementation and validation. Record unperformed tests in coverage and classify their decision impact.

## Pitfalls

- Management profit may omit group costs, financing expenses, or other adjustments.
- Equity movement can reflect contributions, FX, distributions, or reclassifications as well as profit.
- Currency conversions require an explicit rate source and date; never silently mix currencies.
- Cash at a parent may not be legally or operationally available to the borrowing entity.
- Historical results and management forecasts are different evidence types.

## Verification

Headline figures tie to retained source versions, periods do not overlap, and each ratio has a definition. The earnings/cash bridge, covenant headroom and dated liquidity assessment are completed or explicitly unperformed with consequences. Neither reported profit nor nominal undrawn facilities alone support a favorable cash-capacity conclusion.