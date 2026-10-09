---
name: credit-memo-drafting
description: "Draft credit memos and evidence-based lender questions."
version: 0.2.2
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, diligence]
---

# Credit memo drafting

Turn completed diligence work into a concise, cited draft for the user's review. This skill assembles analysis; it does not make an investment commitment or contact a lender.

## When to Use

- Draft or revise a credit memo, decision brief, or consolidated lender questions.
- Do not use a polished memo as a substitute for missing diligence.

## Prerequisites

For a Zivoe preliminary credit memorandum or its Word/letterhead format, also load preliminary-credit-memo. Its factual-only scope, engine/document-analysis handoff and hard six-page cap take precedence over the generic layout and recommendation language below. Do not include an investment recommendation unless separately requested. Retain detailed coverage/issue records separately and keep material limitations visible in the memo. Other explicitly requested decision briefs and standalone lender questions remain in this general skill.

Use the user's supplied template and current writing preferences when available. Inputs may include evidence, financial and structure reviews, engine reports, and questions. Record which inputs actually exist; prior recommendations are not current instructions.

Before creating outputs, load the shared record contract with `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Use its versioned review directory, source/evidence IDs, coverage states and issue dispositions. If running this skill alone, create the minimum records for this scope; do not imply the other topics were reviewed.

## Procedure

1. Establish audience, review_id/date and review scope, including whether the user actually requested a recommendation. The preliminary memo defaults to facts and calculations after analysis, without an approve/decline decision. If no template exists, include executive findings; transaction/borrower; portfolio; financial condition; structure and repayment; documented risks/protections; coverage and unresolved issues. A user template may change layout but must not hide material omissions or blockers.
2. Build a claim checklist linking material numbers/assertions to retained document versions and evidence IDs or exact engine runs. Label source claims, calculations, inferences, scenarios and independent corroboration distinctly. Review the source manifest for changed versions before reusing an earlier finding.
3. Describe engine verdict, AI-review status, methodology, tape date, and coverage separately. Engine PASS means its configured checks passed; it is not credit approval.
4. Include a material-topic coverage table: portfolio/population, repayment, collateral, originator liquidity, structure and servicing as applicable. Show evidence dates, examined/partial/unreviewed/unreadable/not-applicable status, unperformed tests and consequences. Include adverse evidence and source conflicts. Each mitigant needs evidence and limitations; a stated policy or guarantee is not demonstrated effectiveness.
5. Consolidate questions and issues without dropping adverse findings. Deduplicate by underlying issue while retaining citations and history. Each unresolved item must be blocks_recommendation, condition_before_funding, or monitoring, with rationale, evidence needed, and responsible reviewer/owner when known. Critical missing repayment, collateral or liquidity evidence must not be downgraded to a routine condition just to permit a recommendation.
6. Write the draft memo and `lender-questions.md` under the unique review directory without replacing earlier review versions. For a requested recommendation, return insufficient information when material blockers remain. A favorable conditional recommendation requires an evidence-supported credit thesis and genuinely bounded conditions; record both the rationale and conditions. Preliminary hypotheses must remain labeled and separate. Use installed document skills for requested formats; Telegram summaries must retain the conclusion and critical limitations.
7. Check headline claims against exact source versions and calculations against saved results. Ensure no material coverage gap or adverse discrepancy disappears during summarization. State population limits, inferred metric definitions, stale evidence, source conflicts and unperformed repayment/downside tests where material. Keep the analyst's recommendation distinct from any authorized investment decision.

## Pitfalls

- Do not inherit obsolete closing dates, position sizes, recommendations, or author preferences from a prior deal's handoff.
- Missing data is not evidence of favorable performance.
- A failed or absent AI review cannot be described as completed.
- Draft questions are not authorization to email them. Do not create a commitment or submit an investment.
- Do not insert deal-specific facts into reusable skills or carry them into another deal.

## Verification

Every material claim is supported or labeled; cited does not mean independently verified. Coverage and issue dispositions agree with the detailed records. Material blockers produce insufficient information, not an unqualified favorable recommendation. The final short summary retains critical limitations. The output is a draft and no external message or investment action occurred.
