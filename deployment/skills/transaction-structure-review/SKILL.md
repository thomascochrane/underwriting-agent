---
name: transaction-structure-review
description: "Map deal obligations, collateral and protections."
version: 0.2.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, diligence]
---

# Transaction structure review

Describe the economic and documentary structure of a financing. Extract terms and identify unresolved protections; do not certify enforceability, lien perfection, or compliance from document text alone.

## When to Use

- Review offering documents, loan agreements, guarantees, or borrowing-base terms.
- Compare the investment description with the underlying transaction documents.

## Prerequisites

Identify deal channel, relevant parties, and available versions. Use the evidence-review discipline and installed document skills. No market-standard assumption substitutes for an actual clause.

Before creating outputs, load the shared record contract with `skill_view(name="diligence-evidence-review", file_path="references/review-records.md")`. Use its versioned review directory, source/evidence IDs, coverage states and issue dispositions. If running this skill alone, create the minimum records for this scope; do not imply the other topics were reviewed.

## Procedure

1. Map the chain from Zivoe to the issuer or borrower and underlying assets. Distinguish a direct loan, a series note, and a participation. Identify the creditor, collateral owner, guarantor, servicer, and collection-account controller.
2. Extract amount, currency, rate/fees, payment dates, maturity, call rights, amortization, reinvestment, and recourse. Record clause citations and whether each document is draft, executed, amended, or unknown.
3. Build a cited collateral/protection table. Where inputs permit, reconcile dated gross collateral through eligibility exclusions, concentration caps and haircuts to the applicable borrowing base, reserves, debt secured by the pool, and availability or deficiency. Follow the actual contractual order and definitions; do not assume a universal waterfall or double-deduct reserves. Distinguish the offered pool from the originator's whole book.
4. Define every coverage denominator and whether reserves are inside or additional to collateral enhancement. Map primary and secondary repayment sources and priority of cash payments, including servicing/enforcement costs, senior or pari passu claims, shared pools and retained interests. Trace which cash is actually available to this instrument; do not double count it.
5. Compare terms across relevant agreements, amendments, offering summaries, and marketing materials. Identify who benefits from each protection; security at a lower entity does not automatically make the investor's own instrument secured.
6. Review competing debt/intercreditor evidence, revolving and run-off periods, cash release/reinvestment rights, triggers, cure periods, and amortization/enforcement consequences. Compare collection timing with contractual debt service and maturity. Test a supported downside relevant to the deal (slower collections, lower recoveries or interruption of new funding), with explicit assumptions and no automatic refinancing. Use tested tools, not a newly improvised asset-class model. Missing data or capability means the test is unperformed, not passed. A missing filing or consent is unverified, not proven absent.
7. Write `structure-review.md` with the party and payment-priority map, cited terms, dated coverage reconciliation, repayment/maturity analysis, downside results or unperformed tests, and unresolved issues. Withhold favorable repayment or collateral-adequacy conclusions where critical support is absent. Assign issue dispositions using the shared record contract.

## Pitfalls

- Different series may share collateral; do not assume each offering has an isolated pool.
- Claimed guarantees or cash control require the relevant documents and applicability checks.
- Overcollateralization percentages can use different denominators.
- Do not import terms from an earlier deal merely because the originator is the same.
- Unsupported asset classes can still receive document review, but no MCA calculation rules may be applied to them.

## Verification

Each term has a versioned locator or is unavailable. Investor rights and underlying collateral rights remain distinct. Coverage amounts, reserve treatment, payment priority, repayment timing and downside assumptions are explicit or untested. Stated overcollateralization alone never establishes repayment capacity, and legal uncertainty is not converted into assurance.