# Underwriting council review

Date: 2026-10-08 (America/Phoenix)
Scope: seven general diligence and MCA skills in this repository, their documentation, and relevant formulas in the separate underwriting engine.
Method: three independent reviewers covering MCA credit analysis, financial/transaction diligence, and evidence/decision controls; findings reconciled by the lead reviewer against the actual files.
This is a procedural review, not a reassessment of any live borrower or an executed model evaluation. No skill or engine files were changed during the review.

## Assessment

The skills are a useful foundation for analyst assistance and evidence review. They are not yet sufficient to support a decision-ready credit recommendation without additional instructions and behavior testing. They could be used for a clearly labeled limited demonstration once the separately deferred runtime dependencies are available.

Keep the engine's AI mapping and review separate from Hermes. The findings concern how Hermes establishes evidence scope, interprets engine results, and connects the analysis to repayment. No finding requires moving the engine's AI into Hermes.

Authentication, Telegram setup, and the engine connection were intentionally deferred and are not defects in this review.

## Findings

### 1. High: identify the tape population before interpreting historical performance

Location: deployment/skills/mca-tape-analysis/SKILL.md:35 and :43.

The skill records file identity, grain, dates and methodology, but does not require establishing whether the tape contains all originations, only active balances, offered collateral, or a filtered sample.

Failure example: an active-only tape excludes charged-off and paid advances. Its arithmetic passes, but the memo presents its statistics as the originator's historical performance.

Required change:
- Record population definition, funding-date coverage, selection filters, and treatment of paid, charged-off, refinanced, sold or transferred advances.
- Reconcile counts and funded amounts to available independent or broader control totals; state when these are unavailable.
- Distinguish whole-book performance from the specific collateral pool.
- If completeness is unverified, label results as statistics for the supplied population and prohibit whole-book or lifetime conclusions.

This blocks historical credit conclusions, not exploratory analysis.

### 2. High: distinguish inferred/default-stock metrics and contractual returns from realized outcomes

Location: deployment/skills/mca-tape-analysis/SKILL.md:43.
Related safeguard: deployment/skills/mca-underwriting-servicing/SKILL.md:27.

The instruction to explain definitions is helpful but too general for the engine's actual metrics. A standalone tape analysis may never load the servicing skill's renewal-credit warning.

Verified engine behavior:
- underwriter_mca/derive.py:326 describes default timing inferred from a single snapshot.
- underwriter_mca/derive.py:336 identifies default among currently outstanding advances.
- underwriter_mca/analytics/measures.py:77 measures principal outstanding on defaulted advances.
- underwriter_mca/analytics/vintages.py:85 labels curve dates inferred.
- underwriter_mca/derive.py:259 includes renewal credits in amounts applied to RTR.
- underwriter_mca/analytics/measures.py:57 defines MOIC using RTR collected divided by principal funded.
- underwriter_mca/derive.py:434 and :436 calculate simple contractual annualization; the net variant deducts commissions.

Required change:
- Read the run's Definitions and Method before describing each metric.
- Label inferred timing and current default stock explicitly; distinguish them from observed historical default events and realized net losses.
- Do not infer lifetime default incidence, cures, recovery timing, or post-default collections without the required historical events and cash-flow data.
- Present cash collections and renewal credits separately. Explain when MOIC includes noncash renewal credits.
- Describe annualized yield as contractual simple annualization. Commission-net is not net of losses, funding costs, servicing, or all expenses.
- Require dated actual cash flows before claiming cash IRR.

This is an interpretation safeguard; it does not propose changing engine formulas in this task.

### 3. High: connect collateral and transaction terms to repayment

Location: deployment/skills/transaction-structure-review/SKILL.md:27.

The skill extracts protections but does not require demonstrating whether cash reaches this instrument in sufficient amount and before its maturity.

Failure example: a memo repeats stated overcollateralization without determining eligibility deductions, shared collateral debt, priority expenses, or whether collections are released elsewhere.

Required change:
- Identify primary and secondary repayment sources and priority of payments.
- Where supported inputs exist, reconcile gross collateral, exclusions/caps/haircuts, eligible collateral, borrowing capacity, applicable reserves, and debt to availability or deficiency. Avoid subtracting the same item twice.
- Record revolving/run-off periods, release rights, triggers, cure mechanics, and their cash-flow consequences.
- Assess maturity mismatch and at least a clearly identified downside case involving slower collections, lower recoveries, or loss of new funding as relevant.
- Use tested calculation tools with recorded assumptions; do not invent a new financial model inside a prose skill.
- Where data or calculation capability is absent, mark repayment/coverage testing unperformed and withhold a favorable conclusion on that dimension.

### 4. High: require an earnings-to-cash bridge and measurable liquidity headroom

Location: deployment/skills/originator-financial-review/SKILL.md:26.

The skill properly distinguishes entities, periods and restricted cash, but leaves cash conversion and covenant tests too optional.

Failure example: profitable reported earnings coexist with cash-consuming advance growth and reliance on a nearly exhausted warehouse facility; the narrative still describes the originator as financially strong.

Required change:
- Bridge reported earnings to recurring earnings and cash generation with sourced adjustments.
- Keep funding costs, commissions, losses/provisions, receivables growth, intercompany flows and distributions distinct where applicable.
- Align dated obligations with unrestricted cash and demonstrated facility availability at the correct entity.
- Calculate applicable covenant headroom using actual definitions, or mark it untested.
- Assess a supported funding-interruption or slower-collections scenario.
- Keep originator survival and borrower-SPV repayment as separate conclusions.

### 5. Medium: carry review coverage and decision blockers into the memo

Locations: deployment/skills/diligence-evidence-review/SKILL.md:25 and :40; deployment/skills/credit-memo-drafting/SKILL.md:22 and :31.

A memo can cite every included claim correctly yet omit material areas that were never examined. The instructions also do not require distinguishing ordinary follow-up questions from gaps that prevent a recommendation.

Required change:
- Define document/section states: unreviewed, partially examined, examined, unreadable, and not applicable with rationale.
- Record reviewed page/sheet ranges, omissions, source date, and consequences of missing evidence.
- Carry a compact topic-coverage table into the memo: portfolio, repayment, collateral, financial condition, structure, and servicing as applicable.
- Classify unresolved issues as blocks recommendation, condition before funding, or monitoring item, with rationale and evidence needed for closure.
- Allow "insufficient information" as the explicit result. A preliminary hypothesis must remain separate.
- A cited source claim is not independently verified merely because it is cited.

### 6. Medium: preserve source versions and review history

Locations: deployment/skills/diligence-intake/SKILL.md:26 and :30; deployment/skills/diligence-evidence-review/SKILL.md:26.

The intake uses optional hashes for duplicates, while general evidence and memo outputs use fixed filenames. A replacement document with the same filename can change what an old citation means.

Required change:
- Hash relied-upon source versions and record receipt/review identity.
- Use a unique review directory and input manifest, retaining stable deal/document-version IDs.
- Link memo claims to the specific evidence version and preserve previous discrepancies and their resolution.
- Extend the tape skill's existing unique-run approach to general review artifacts.

### 7. Before decision use: test underwriting behavior with a synthetic deal

Location: docs/skills.md, Review scenarios and Automated checks.

The documentation correctly states that passing checks cover installation, not underwriting behavior. This is an acknowledged readiness limit, not a false claim that underwriting was validated.

Create a small synthetic pack and evaluate both required findings and prohibited claims:
1. An active-only tape with missing charge-offs: no whole-book loss conclusion.
2. Renewals that make applied-to-RTR MOIC exceed cash realization: separate the two.
3. Inferred default timing and contractual yield: no claim of observed lifetime losses or realized IRR.
4. Reserve already inside collateral enhancement: no double counting.
5. Profitable management accounts with cash burn and restricted/conditional funding: surface liquidity limitations.
6. Amendment changing priority or eligibility: preserve and resolve the conflict.
7. Unreadable appendix or stale tape: propagate partial coverage into the memo.
8. Engine PASS with failed AI review: preserve both states.
9. Updated statement under the same filename: retain the original evidence version.
10. Material repayment evidence missing: return insufficient information rather than an unqualified favorable recommendation.

Evaluate intermediate records and the final shortened memo. Review outputs with a human credit analyst; correct arithmetic and clean installation alone are insufficient.

## Lower-priority improvement

For servicing evidence, record sample population, selection method, count, period and exception rate when available. A few favorable sample files should not substantiate a claim about universal policy adherence. See deployment/skills/mca-underwriting-servicing/SKILL.md:26.

## Strengths to retain

- Source facts, calculations, inference, and missing evidence are distinguished.
- Entity, reporting-period and currency differences are explicit.
- OCR uncertainty and source conflicts remain visible.
- Prior memos and unrelated deals are not treated as current authority.
- Engine PASS, AI-review status, workbook recalculation and credit approval are distinct.
- Credit rules remain in engine configuration rather than copied into skills.
- Draft lender questions do not authorize sending messages.

## Suggested order

1. Tighten the MCA population and metric interpretation instructions.
2. Add topic coverage and recommendation-blocker conventions.
3. Require supported repayment/downside, cash conversion and headroom analysis; explicitly mark unavailable tests.
4. Add versioned evidence and review manifests.
5. Run the synthetic cases after the model connection is available.

No changes were committed or pushed as part of this review.