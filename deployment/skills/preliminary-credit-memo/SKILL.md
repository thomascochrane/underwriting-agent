---
name: preliminary-credit-memo
description: "Write Zivoe preliminary credit memoranda in Word."
version: 0.1.0
author: Thor Abbasi, OpenAI Codex
license: Proprietary
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [underwriting, diligence, memorandum]
---

# Preliminary credit memorandum

Produce a preliminary credit memorandum that reads like the work of an experienced credit analyst, as a Word document on supplied Zivoe letterhead. Produce a web version only when asked. These standards capture the user's Jaguar / LPA memo lessons; those prior deals supply no facts or conclusions for a new transaction.

## When to Use

- Draft or revise a Zivoe preliminary credit memorandum, including a request for a Word memo, letterhead, or this house style.
- Use credit-memo-drafting for the shared evidence and decision discipline. This skill governs the preliminary memo's structure, voice, presentation and review. It does not change credit policy or authorize an investment.
- Apply general standards across asset classes. Use listed-security exhibits only where the actual collateral supports them; do not impose share trading-volume or Rule 144 assumptions on MCA or other receivables.

## Prerequisites

Load credit-memo-drafting and its shared evidence-record contract. Read [references/memo-standard.md](references/memo-standard.md) before drafting, and [references/review-council.md](references/review-council.md) before review. Use the installed document-creation/rendering tools, after checking that they are available in this runtime; do not assume desktop-only tools exist on the server.

Establish the transaction, requested as-of date, source inventory, current standing constraints and authentic letterhead asset. No letterhead image is bundled with this skill. Obtain the supplied approved asset before calling a document letterheaded; never invent the logo or imply an unavailable asset was used. Analytical work can proceed while presentation inputs are missing, but disclose the unfinished deliverable.

## Procedure

1. Read every supplied source document in full before drafting: proposed or expected terms, all financial statements and every note, legal memoranda, cap tables, and arranger emails and attachments. Reconcile page counts, appendices and extraction coverage with the source register. For spreadsheets, inspect every relevant sheet, definitions and notes and use reproducible whole-population checks, not selected rows alone. A prior summary, search snippet or engine report is not a replacement for source review. If something is unreadable or missing, record the gap and seek the material; deliver a limited working draft only if the user requests one, visibly stating its coverage and consequences.
2. Read financial notes line by line. Look for going-concern/liquidity disclosures, related-party balances and the explanation of amounts due from affiliates, cash-restricting distribution waterfalls, member/insider notes, investor defaults, and expired commitments. Quote the note that explains a balance, with a locator; do not speculate about its composition. Test whether each repayment source is actually available to the Borrower, including restricted distributions and reimbursements that are not fee income.
3. Check terms for internal inconsistencies, including currency, lender names and carryover text. Surface material inconsistencies early in the Summary and Transaction overview. Attribute management, arranger and advisor claims. Verify current-world assertions such as closings, filings, assets under management and ownership against dated primary sources; retain the verification evidence. If current verification is unavailable, say so and assess the consequence instead of implying it occurred.
4. Build reproducible exhibit calculations and a claim-to-evidence checklist. Record exact market figures, source, observation window and as-of date; never replace those with a rounded typical-day estimate. Define constructed ratios and their entity/debt perimeter. Show coverage and loan-to-value together using consistent valuations, dates and exposure definitions. Label all inferences, Zivoe estimates and illustrative assumptions. For engine outputs, inspect the exact job, run report, mapping provenance, warnings and actual AI-review status; technical review is an input to the memo, not a credit recommendation.
5. Draft to the structure and style in memo-standard.md. The user's requested layout controls the reader-facing memo. Retain the shared detailed coverage and issue records alongside it, and integrate material limitations into the relevant sections and recommendation. No separate Open questions or What changed section belongs in the memo. Lender questions and review findings remain separate companion records.
6. Give a supported preliminary recommendation, or insufficient information if material blockers remain. Do not recommend an exact facility amount or margin-call trigger level. This restriction does not prohibit accurately quoting sourced proposed terms in the terms table or using a clearly identified exposure for coverage/recovery calculations. Describe actual mitigants and their limits. Conditions cannot conceal unresolved repayment, collateral or liquidity blockers.
7. Run the separate-agent review council described in review-council.md, with the draft, source evidence and Thor's standing constraints. Check reviewer claims against sources and calculations. Record each finding as applicable or not applicable with a reason; apply applicable findings and report remaining unverified items separately to Thor. A reviewer assertion is not new verified evidence. If independent agents are unavailable, report the council as incomplete; a single agent's role-playing does not count as separate reviewers.
8. Generate the numbered Word revision on the supplied letterhead, render it, inspect every page, and verify no more than eight pages. Repeat rendering and page-count checks after every content or layout change to a Word revision, including council corrections. Leave a few lines of slack on the last page because Microsoft Word may paginate longer than LibreOffice. Without a renderer, do not claim the page limit or visual checks passed. Follow the trimming order in the standard, preserving core exhibits.
9. Preserve every prior version. Save a new numbered file such as preliminary-credit-memo_01.docx, _02.docx, using the next unused number. On Thor's computer, use his actual accessible Downloads directory as requested, retaining the evidence linkage. In the deployed Linux container, save under the deal's versioned review/output directory in /workspace and return the file through the authorized conversation; do not claim it was saved to Windows Downloads or mount the host to achieve that. Record the difference in the handoff. Optional web output follows the same claims, dates, revision and confidentiality markings.

## Pitfalls

- Do not import a prior deal's assumptions or legal conclusions. The listed-security recovery convention is a conditional scenario, not a liquidity guarantee or general receivables method.
- Legal mechanics remain conditional on the sourced facts and required steps. Do not state a fixed Rule 144 sale-volume allowance as certain. The legal reviewer flags mechanics and dependencies; a separate legal opinion is out of scope unless Thor requests it.
- No invented fourth strength, invented market exhibit, filler mitigant, or unsupported favorable conclusion to satisfy a layout.
- No em dashes in memo prose, tables, chart labels, headers or footers. Do not silently alter a verbatim quotation to remove one; select a faithful shorter quote or paraphrase with attribution instead.
- Completion of an engine job does not automatically start drafting or the council. This skill supplies instructions, not an automatic post-job workflow. Neither skill installation nor a generated DOCX establishes rendered or model-tested behavior.

## Verification

Confirm full-source coverage or an explicitly requested limited scope, dated claim provenance, reproducible calculations, actual engine AI status, accurate terminology, real mitigants, and visible material limitations. Check all required exhibits or documented asset-class substitutions, source/as-of lines, letterhead, footer, revision uniqueness, and rendered page count after the final change. Report council coverage, dispositions and any unverified figures outside the memo. Deliver a preliminary draft, separate companion findings/questions as needed, and no external lender communication or investment action.
