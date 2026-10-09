# Engine and document analysis handoff

The intended memo is the synthesis of analyzed engine output and the other supplied deal materials. It is not the engine's automatic result ZIP, a transcript of its AI review, or a summary written before the source review is complete.

Before drafting the normal memo, save a memo-handoff.md in the versioned deal review directory with:

- Exact engine job ID, asset class, revision, input/config identities, tape date and population. Inspect retained artifacts and run report, not just Telegram's completion message. Record validation status, missing analytics and whether the engine's AI mapping/review actually completed, failed, was skipped or is unknown. Never treat PASS as investment approval or evidence that all AI work completed.
- An account of the engine findings Hermes actually checked: units, denominators, period coverage, methodology, material tie-outs, warnings and relevant calculations. Distinguish engine output from source truth and label inferred rather than observed performance. Include file/section/sheet locators.
- Supplied-document register and full-reading coverage, including financial notes, appendices and relevant email attachments. Document-analysis checkpoints must contain findings and evidence, not merely filenames. Distinguish missing requested documents from unread portions of supplied documents. Material absent documents remain visible limitations even when every supplied file was reviewed.
- Cross-source reconciliation between the engine/tape, financial statements, terms and other materials. Keep unresolved differences with exact source identities; do not silently choose the more favorable number or mix unrelated dates and populations.
- List of factual statements ready for the memo, supporting calculation/evidence IDs, material limitations and source/as-of dates. Recommendations from an engine model, old memo or counterparty must not silently become Hermes's conclusion.

Queued/running jobs and unreviewed supplied materials are not a completed handoff. Resume the outstanding analysis rather than presenting the normal final memo as ready. If an engine job fails or omits analytics, diagnose and record what is missing. A user-requested limited working memo can describe available evidence and the precise limitations; it cannot claim the failed or omitted work ran. An unsupported asset class must not be analyzed using MCA methods to satisfy this prerequisite.

After the handoff, synthesize the factual Word memo, run the review council, apply supported corrections and verify the final rendered page count. The memo may state what cannot be determined, with reasons; it does not issue a decline or approve decision. Internal issue labels such as blocks_recommendation retain their audit meaning without implying a recommendation is being requested or delivered.

The existing job notifier sends engine outputs independently. It does not wake Hermes, perform document review or generate this memo. Until a completion orchestrator is implemented and tested, a subsequent user request or separately configured workflow must resume Hermes with the job ID and saved review checkpoint. Never promise automatic end-to-end delivery solely because this skill is installed.
