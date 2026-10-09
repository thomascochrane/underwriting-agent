# Zivoe output branding

All human-facing files Hermes creates for delivery use the supplied Zivoe letterhead. This includes the credit memo, diligence summaries, questions, monitoring reports and supporting presentations or spreadsheets. This is a presentation rule, not permission to change engine calculations, source documents or evidence.

## Word templates

- General letterhead: `/deployment/branding/zivoe-letterhead.docx`. Blank body, US Letter layout, Arial styles, repeating authentic artwork, a simple confidentiality footer and editable creation-date placeholder.
- Credit memorandum: `/deployment/skills/preliminary-credit-memo/assets/zivoe-credit-memo-template.docx`. The skill installer also supplies it at `/opt/data/skills/zivoe-underwriting/preliminary-credit-memo/assets/zivoe-credit-memo-template.docx`. Six required sections, a terms table, editable placeholders and memo footer.

Copy the appropriate DOCX to the deal's output directory and edit that copy. Do not overwrite the repository template or rebuild the layout from the JPEG when the Word template is available. Preserve section settings and header/footer relationships. If clearing the body programmatically, keep the final `w:sectPr`. Replace bracketed instructions and dates; apply Normal style to completed body prose so placeholder italics/gray do not remain. Keep real source references beside factual findings.

The entire footer is **Confidential · As of [creation date]** on every page. Fill the placeholder with the creation date of the delivered document revision, using a full month name. Keep that date fixed; do not use a field that changes each time the file opens. No draft/internal labels, NDA statement, pricing dates, page numbers or additional disclaimer belong in the footer. Source-data and price observation dates remain in the relevant body text, tables or exhibits.

The blank template is one page; the memo skeleton is two pages. These are starting layouts, not completed reports. The memo's break before Collateral and portfolio analysis can be moved or removed when populating it. The completed memo still targets five pages with a six-page maximum including Sources and exhibits. Render every completed revision again after filling or changing layout.

Both templates were exported with Microsoft Word on Windows and all three resulting pages were visually checked on October 9, 2026. The repeating artwork, simplified confidentiality/creation-date footer and terms table passed that check. This does not establish server-side rendering availability or the page count of a future completed memo. No reference-deal body content, recommendations, comments or macros are included.

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
