# Council remediation: skill version 0.2.0

The 2026-10-08 council review remains the historical assessment of version 0.1.0.

| Finding | Implemented change | Remaining validation |
| --- | --- | --- |
| Tape population | MCA skill requires population/filter history and reconciliation; blocks whole-book claims from incomplete populations | Synthetic active-only case; live agent evaluation pending |
| Metric interpretation | Explicit snapshot/default-stock, noncash renewal MOIC, contractual yield and IRR distinctions | Fictional stored report with known outputs |
| Repayment and downside | Structure skill requires coverage, priority, maturity and supported downside analysis or explicit unperformed status | Validate future calculation integrations separately |
| Earnings/cash and headroom | Financial skill requires cash bridge, actual availability, covenant definitions and supported funding-interruption analysis | Fixture cash gap and unavailable-funding case |
| Coverage and decision blockers | Shared coverage/evidence/issue schemas; memo requires insufficient-information disposition when critical blockers remain | Verify both full memo and short summary with a model |
| Source versioning | Hashed retained versions and unique review directories; cross-review identities and retained discrepancy history | Same-filename changed-source case |
| Behavioral testing | Fictional inputs plus ten-item human-scored rubric, isolated from runtime skills | Model-backed scoring has NOT run |
| Servicing sample limits | Sample population, selection, count, period and exceptions required; no generalization from favorable samples | Missing and management-selected sample case |

The engine and its AI backend remain unchanged. These are instructions and supporting review conventions, not enforcement of an automated credit policy. No approval thresholds or investment permissions were added.

The skill installer now records installed hashes and upgrades only matching managed copies (or the exact known 0.1.0 baseline). It backs up replaced skill trees in the Hermes state volume, preserves unrelated skills, and rejects conflicting edits before any skill changes. The fixtures and scoring rubric are mounted only for offline fixture tests, not into the Hermes service.

Authentication and engine connectivity remain deferred. Passing offline checks establishes file validity, update behavior and fixture consistency; it does not establish underwriting quality.