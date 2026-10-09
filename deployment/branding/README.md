# Zivoe output branding

All human-facing files Hermes creates for delivery use the supplied Zivoe letterhead. This includes the credit memo, diligence summaries, questions, monitoring reports and supporting presentations or spreadsheets. This is a presentation rule, not permission to change engine calculations, source documents or evidence.

## Shared asset

Use `/deployment/branding/zivoe-letterhead.jpg`. The repository copy is `deployment/branding/zivoe-letterhead.jpg`. It is the authentic blank artwork extracted from the supplied reference, with no deal text or EXIF tags. Dimensions are 2448 x 3168; SHA-256 is `823208a646fc93efe511895ac3569c1164470e8d049ada6b7cb4eaa04c4ec560`. Preserve these image bytes. The matching copy in the preliminary-credit-memo skill remains for portable skill installation.

## Apply by format

- Word and PDF reports: full-page repeating letterhead behind content on every page. Use portrait US Letter, start with 1.35-inch top, 1-inch side and bottom margins, and check every rendered page. Exact Word anchor geometry is in the memo skill's `references/letterhead.md`. The six-page cap applies to the credit memo, not all supporting reports.
- Spreadsheets: use a dedicated Zivoe letterhead cover sheet and branded print headers/footers on reporting sheets. Keep usable column widths, existing formulas, cached results, ranges and engine worksheet names intact. Do not insert decorative rows into data tables. Work on a clearly labeled presentation copy; retain the original engine workbook and record its hash. Render the cover and representative printed report pages before delivery.
- HTML reports and slides: use the same artwork in an appropriately sized page/canvas, preserving its aspect ratio and leaving the logo/rules clear. Embed the asset in standalone HTML rather than relying on an unavailable container path. Do not stretch a portrait page to fill a landscape canvas.
- CSV, JSON, YAML and other machine-readable files: preserve their schema and data. Supply a letterheaded companion index/report describing those files, provenance, dates and limitations; never insert logos, title rows or comments that break the format. ZIP archives include the branded index and individually formatted human-facing deliverables.
- Retained third-party evidence, original engine artifacts and internal logs remain originals. Do not add Zivoe letterhead to a lender's source document or present it as authored by Zivoe. A raw engine artifact is not a finished branded report.

Use the actual transaction title, revision, as-of date and appropriate confidentiality marking. Do not inherit dates, deal facts or recommendations from the reference memo. Never label material as under NDA without a basis. The memo's specific formatting instructions also apply to memo deliveries.

## Delivery verification

Before returning a finished file, check that branding is visible, body text and charts clear the artwork, and the output is readable. Record the rendering tool and any unavailable checks. When making presentation copies, reconcile data and formulas against the originals; a branding failure does not authorize regenerating financial results. Report a missing asset or renderer instead of claiming completion.

The shared asset and instructions are available through the existing read-only deployment mount. They do not install a renderer or automatically transform engine-worker outputs. The notifier currently sends a raw engine-results ZIP before Hermes resumes; identify it as an intermediate engine package. Hermes must apply this standard when assembling the final diligence deliverables. Automatic branding of that intermediate worker package requires a separate tested formatting stage.
