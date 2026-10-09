# Review record contract

These records apply to a full review or a single-skill review. They track evidence and analytical coverage; they do not automate approval or enforce a credit policy.

## Location and identity

Choose a deal_id for the actual transaction and a new review_id for each review/revision. Work under a unique directory such as <deal>/reviews/<review_id>/; do not reuse another review's output files. Record the actual review timestamp and timezone. A single-skill run leaves other material topics explicitly unreviewed.

Hash relied-upon source bytes using SHA-256 before analysis. Preserve their exact bytes in a sources/ subdirectory, or use a genuinely immutable source reference. A live filename, URL, or shared-drive location is not immutable. Record receipt time if known separately from ingestion and document/report dates; unknown receipt time stays unknown. Rehash before publishing if a live working source was used; reconcile changes before citing it.

Use a stable document_id for a logical document and document_version_id for each content version, based on the document identity plus content hash. Same filename with new bytes is a new version. Identical bytes with different filenames can be duplicates. Evidence IDs are stable within a review; cross-review references always include review_id. Never put confidential deal records into the reusable skill directory or Git.

## input-manifest.json

Required fields:
- deal_id, review_id, review_timestamp, review_timezone, scope
- documents: array of document_id, document_version_id, original_relative_path, retained_source_path_or_immutable_reference, sha256, size_bytes, received_at (null if unknown), ingested_at, document_date, entity, source_role
- previous_review_id: null or prior review being extended

Keep the manifest with the outputs. Do not overwrite prior manifests. Record transformations (OCR, extraction, normalization) with tool/version where available and links to the original document version.

## document-register.csv

Columns:
document_id,document_version_id,original_relative_path,retained_source,sha256,source_role,topic,document_date,entity,version_status,duplicate_of,review_status,limitation

Source roles include original_source, management_claim, arranger_claim, prior_analysis, generated_output. Version status includes draft, executed, amended, superseded, unknown; a filename alone cannot establish it.

## coverage.csv

Columns:
review_id,topic,document_version_id,required_scope,examined_ranges,omitted_ranges,source_as_of,status,consequence,issue_ids

Allowed states:
- unreviewed: not examined
- partial: some required pages/sheets/sections or tests remain unexamined
- examined: the stated scope was examined, not necessarily verified or adequate
- unreadable: extraction/reading failed for the required scope
- not_applicable: give a transaction-specific reason

Include topic-level rows for portfolio/population, repayment, collateral, originator financial condition/liquidity, structure, and servicing as applicable even when no document exists. Record unperformed tests and stale evidence with their consequences. Staleness uses applicable policy or stated judgment, never invented universal cutoffs. A full document is not examined because selected pages were read.

## evidence.csv

Columns:
review_id,evidence_id,document_version_id,locator,claim,classification,entity,period_or_as_of,currency,units,definition,verification_status,verification_basis,calculation_reference,limitation

Classifications: source_claim, calculated, inference, missing.
Verification statuses: source_only, corroborated, reproduced, unresolved.
A cited claim is source_only unless its stated verification_basis demonstrates more. Reproduced means the calculation was reproduced, not that its inputs are independently correct. Corroboration must identify the independent evidence. Use multiple rows/linked evidence IDs for claims with multiple sources.

Save calculation inputs, formula/script or workbook reference, tool/version where relevant, assumptions, and output. Distinguish scenarios from forecasts. Do not manufacture unavailable calculations.

## issues.csv and discrepancies.md

Columns:
review_id,issue_id,topic,finding,evidence_ids,decision_impact,disposition,status,evidence_needed,owner,resolution_evidence_ids,resolution_date

Disposition:
- blocks_recommendation: insufficient evidence or a material unresolved issue prevents a supported credit recommendation
- condition_before_funding: a bounded, specified condition compatible with an already supported credit thesis
- monitoring: an ongoing observation with a stated trigger or next review

Assign with reasons; neither all missing items nor all questions are automatically blockers. Critical unknowns about repayment, collateral or liquidity cannot be relabeled as conditions to avoid an insufficient-information result. Use the user's applicable policy when supplied; do not invent numeric approval thresholds.

Statuses: open, resolved, superseded. Keep the original finding and append resolution evidence/date. A lender reply is a new claim until checked. Issues cannot disappear merely because a memo is shortened.

## Memo handoff

Include review_id, source-manifest reference, material-topic coverage, as-of dates, outstanding issue dispositions, and links to exact engine runs. State insufficient information when blockers remain. Distinguish a preliminary hypothesis, an analyst recommendation, and a final human decision. Short chat summaries must retain the conclusion and material limitations.