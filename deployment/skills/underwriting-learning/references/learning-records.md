# Persistent learning records

Store private runtime history under `/workspace/underwriting-learning/`, never in Git or installed skill folders. Use the shared evidence contract for source versions and review records. Hermes memory may point to this directory; detailed records remain here and are retrieved when relevant.

## Layout

- `cases/<deal_id>/events/<event_id>.json`: one immutable event per original assessment, decision, feedback, reporting update, correction or outcome.
- `lessons/<lesson_id>/<version_id>.json`: immutable lesson versions.
- `index.json`: a rebuildable list of event/lesson paths and current lesson versions. Rebuild by scanning records if absent; the index is not evidence.

Use safe generated IDs as path components. Write a new record to a temporary file and atomically rename without replacing an existing event. Check source hashes, period and event type before adding a duplicate. A corrected report is a new version linked through `supersedes`; keep the old record. If concurrent writers are possible, serialize updates or rebuild the index instead of overwriting another writer's work.

## Event fields

Include `event_id`, `deal_id`, `event_type`, `recorded_at`, `effective_as_of`, `available_at` (null if unknown), `review_id`, `supersedes` (null for initial event), `asset_class`, `originator`, `facility`, `cohort_or_population`, and `sources` containing document_version_id, retained source path/hash and evidence locator.

Store applicable content as structured fields:

- `baseline`: original assumptions/forecasts, horizon, methodology/engine version, agent recommendation, uncertainty and unresolved issues.
- `human_decision`: decision, decision date, decision-maker/source, and reason if provided. Unknown values stay null.
- `observations`: metric, value, units/currency, numerator/denominator or formula reference, reporting period, definition, source, verification status and limitations. Distinguish interim from final outcomes and forecast from actual.
- `feedback`: exact correction or preference, attributed source/date, affected claim and supporting evidence. A preference is not an empirical credit finding.
- `lesson_applications`: lesson ID/version, reason applicable, limitations, review actions taken and any later evidence of usefulness.

Do not backfill `available_at` with a document's printed date. If historical availability is unknown, exclude it from claims of prospective validation.

## Lesson fields

Include `lesson_id`, `version_id`, `created_at`, `supersedes`, `statement`, `scope`, `status` (candidate, supported, contested, withdrawn), `supporting_event_ids`, `contradicting_event_ids`, `independent_deal_count`, `originator_count`, `observation_horizon`, `evidence_strength_and_limitations`, `exceptions`, `suggested_review_action`, and `policy_change_proposal` (null unless proposing a separate change).

'Qualified support' is a judgment explained by evidence, not an arbitrary minimum case count. Specify repeated observations within one deal separately from independent deals. A supported lesson remains revisable. Record any policy approval separately with its source and effective date; lesson status does not confer policy authority.

## Demo acceptance cases (live evaluation pending)

- Three weekly reports from one deal: three reporting events, one independent deal; no claim of proven general predictive power.
- A revised report changes collections: retain both source versions and supersede the observation; do not double-count collections.
- A reviewer approves a deal without performance data: record the decision, leave realized outcome unknown.
- Renewal credits explain a falling MCA balance: do not learn that the same amount was cash collected.
- A new comparable deal arrives: retrieve applicable lessons, cite their history, and test current documents independently.
- A later default contradicts an earlier favorable hypothesis: preserve both, revise the lesson and identify what was knowable at the original date.
