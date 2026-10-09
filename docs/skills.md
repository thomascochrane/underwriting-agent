# Underwriting skills

Eleven custom skills (versions recorded in their frontmatter) are versioned in `deployment/skills/`. These are procedural instructions for the current underwriting profile, not separate agents or profiles. The existing engine retains its AI mapper and reviewer.

| Scope | Skill | Expected output |
| --- | --- | --- |
| General | diligence-intake | Document register and missing-evidence list |
| General | diligence-evidence-review | Cited evidence ledger and discrepancies |
| General | originator-financial-review | Financial review with traceable calculations |
| General | transaction-structure-review | Party/obligation map and cited deal terms |
| General | credit-memo-drafting | Draft memo and consolidated lender questions |
| General | preliminary-credit-memo | Factual Zivoe Word memo, maximum six pages, after engine and document analysis |
| General | portfolio-performance-review | Reporting variances and original-thesis monitoring |
| General | underwriting-learning | Persistent case history and evidence-linked lessons |
| General | engine-jobs | Persistent engine submission, status and delivery tracking |
| MCA | mca-tape-analysis | Engine run summary, artifacts and limitations |
| MCA | mca-underwriting-servicing | Policy/practice review and focused questions |

The general skills apply across asset classes at the document-review level. Only MCA-specific analytical procedures are included. Consumer-credit and medical-receivables methodologies are outside this skill set.

## Install and validate

With the gateway stopped:

```powershell
.\scripts\hermes.ps1 -Action Skills
.\scripts\hermes.ps1 -Action Test
```

Skills copies the validated definitions into `HERMES_HOME/skills/zivoe-underwriting/` in the Docker state volume. It works before model login or Telegram setup. It leaves bundled and unrelated skills alone and is idempotent. Upgrades are allowed only when installed files match recorded managed hashes or the exact known 0.1.0 baseline. Replaced skill trees are backed up under HERMES_HOME/skill-backups/zivoe-underwriting/. Conflicting local edits stop the operation before skill changes; reconcile them deliberately. There is no force/overwrite mode.

Run Skills on fresh deployments as well as this existing deployment. Initialize does not implicitly install or update skills. The Skills action performs the checked upgrade. Start a new Hermes conversation after installation so its skill catalog refreshes.

## Current capability boundaries

- The engine-jobs skill uses the optional worker overlay and checks its heartbeat before submission. Engine authentication is a separate prerequisite for AI-assisted runs.
- Engine AI authentication is separate from Hermes authentication. No model or Telegram credentials are added by skill installation.
- PDF/Word/Excel handling builds on bundled skills and available tools; availability of instructions alone does not prove OCR or every dependency works.
- No live deal folder is mounted by this change. Outputs stay under the selected accessible deal directory.
- No autonomous full-deal workflow, email sending, additional profiles, or new engine calculations are installed.
- Credit rules are read from engine configuration and actual run outputs rather than embedded as fixed numerical rules in skill prose.
- Engine channel, credit-methodology profile, and workbook presentation profile are distinct from a Hermes profile.

## Review scenarios

These are behavior acceptance cases for a future model-backed demo. They have been reviewed against the instructions; they are not completed live-agent evaluations.

| Input scenario | Required behavior |
| --- | --- |
| Folder includes source documents, duplicate downloads, and an old memo | Preserve files; distinguish source from prior analysis; do not inherit the old memo's decision |
| PDF is image-only and OCR is unavailable | Mark relevant pages unreviewed; no claim of a completed review |
| Management earnings omit expense lines | Keep omissions visible; do not treat blanks as zero |
| Reserve may sit inside stated collateral enhancement | Check the definition and denominator before adding it |
| User requests MCA analysis but the engine is absent | Report engine connection pending; no synthetic workbook or fabricated run |
| Engine PASS but AI review failed | Report both states; do not call it fully AI-reviewed or credit-approved |
| Tape is a medical-receivables or consumer portfolio | Allow general document review; do not apply MCA rules |
| Two runs use different seasoning or default definitions | Identify methodology differences before comparing performance |
| Renewal credit appears with cash collections | Preserve the distinction and ask a cited question if unresolved |
| User asks for lender questions | Create a draft; sending requires explicit authorization |

Automated checks cover the pinned Hermes frontmatter validator, installation, repeat installation, conflicting local edits, invalid inputs, and skill-name collisions. They do not establish underwriting quality or authenticated connectivity.
## Council changes and evidence records

Version 0.2.0 addresses population completeness, metric interpretation, repayment/downside,
cash conversion and liquidity headroom, topic coverage, decision blockers, source versions,
and servicing sample limitations.

All skills use the [shared review record contract](../deployment/skills/diligence-evidence-review/references/review-records.md).
A unique review directory retains source hashes/versions, manifest, evidence, coverage and
issues. A cited statement is not automatically independently verified.

The [synthetic evaluation pack](../evaluation/README.md) contains fictional inputs and a
separate reviewer rubric. The Test action checks fixture arithmetic and consistency.
The fixture is not mounted into normal Hermes conversations and the rubric must be withheld
from a future model-backed evaluation. That evaluation remains NOT RUN.
The earlier CRM/person-specific workflows are not part of this deployment. Only the eleven underwriting skills are custom-installed; generic upstream skills, including document handling, remain available.

## Learning and ongoing reporting

The new skills record original assessments, reviewer feedback, decisions and later performance separately. Private case events and versioned lessons live under /workspace/underwriting-learning/; deal evidence remains in the versioned review directories. Future reviews retrieve relevant lessons without treating another deal as current evidence. Weekly reports update the history when supplied; no reporting feed or recurring job is configured.

This is persistent case-based learning, not model retraining. Learned hypotheses can guide review questions; changing credit policy or engine rules requires a separate recorded decision. Predictive improvement is unproven until tested on later unseen outcomes. See the learning skill reference for live-demo acceptance cases; authenticated behavioral evaluation remains pending.

## Preliminary credit memorandum

The preliminary-credit-memo skill uses the supplied example as a rough presentation reference. It targets five pages with a hard six-page limit including exhibits and Sources, and defaults to factual findings with no recommendation, decision/counter-proposal or suggested funding conditions. It requires Hermes to inspect the engine results, finish supplied-document analysis and reconcile the sources before normal memo drafting. A new handoff reference records that readiness. Full financial-note review, analyst voice, source-dated exhibits, authentic letterhead, numbered revisions and five independent review roles remain. Reviewers check factual completeness rather than proposing an investment decision. The general memo skill routes to this format. Detailed coverage and issue records remain outside the reader-facing memo; material limitations still appear in its factual findings. The exact section arrangement remains a working structure for refinement with the user.

The listed-security price/holders/recovery conventions are conditional. MCA and future asset classes use supported class-specific exhibits. The 25% daily-volume scenario is not an MCA credit rule or an observed fact; include it only if such a scenario is supplied or requested for the deal. Sourced proposed terms, contractual protections and necessary calculation inputs remain allowed, with their status clear. Detailed engine workbooks and audit records are separate supporting files, not appended pages to evade the six-page cap.

No letterhead asset, document renderer, reviewer runtime or automatic completion callback is installed by adding these instructions. The skill checks availability and reports missing prerequisites. Server revisions live in the deal workspace and are returned through the authorized conversation; Windows Downloads is used only when actually accessible on Thor's computer. Full memo generation, pagination and the independent council still require a model-backed end-to-end test.
