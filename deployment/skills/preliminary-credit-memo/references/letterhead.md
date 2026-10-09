# Required Zivoe letterhead

Use a copy of assets/zivoe-credit-memo-template.docx as the starting Word memo. It already embeds assets/zivoe-letterhead.jpg on every page and includes the original editable footer notice, `Contains information received under NDA`. Replace the date and price-date placeholders while retaining the notice and dynamic PAGE field. The template is available relative to this skill directory, or at /deployment/skills/preliminary-credit-memo/assets/zivoe-credit-memo-template.docx. For a general blank Word document, use /deployment/branding/zivoe-letterhead.docx. The placement details below explain the existing template geometry and are a fallback for other output formats; do not rebuild the Word header unnecessarily. This is the original blank letterhead image embedded in the user's supplied reference memo, extracted without modifying its image bytes. It contains the Zivoe logo and page rules, with no transaction text. The reference memo's body, charts, dates, recommendations and metadata are not bundled or reused.

## Asset identity and access

- Relative path: assets/zivoe-letterhead.jpg.
- Deployed path: /opt/data/skills/zivoe-underwriting/preliminary-credit-memo/assets/zivoe-letterhead.jpg.
- Repository source: deployment/skills/preliminary-credit-memo/assets/zivoe-letterhead.jpg.
- JPEG dimensions: 2448 by 3168 pixels, matching US Letter's aspect ratio.
- SHA-256: 823208a646fc93efe511895ac3569c1164470e8d049ada6b7cb4eaa04c4ec560.
- No EXIF tags. Do not alter, crop, recolor, regenerate or replace the asset silently.

Use the available terminal/file tools to pass the actual image path to the document builder. A skill_view text response is not the binary image. On a different deployment, resolve this path relative to the installed skill directory. Verify the asset exists before drafting the Word file; an inaccessible image is an installation issue, not permission to omit the letterhead.

## Placement

Use portrait US Letter, 8.5 by 11 inches. Place the image in the repeating header, floating behind text and positioned at the page origin, not the margin origin. Set its dimensions to the full page without changing aspect ratio. The reference uses a DrawingML wp:anchor with behindDoc=1, wrapNone, horizontal and vertical positions relativeFrom=page at zero, and an extent of 7772400 by 10058400 English Metric Units. An inline image in the body is not equivalent.

Ensure the header repeats on every page and across sections. Either disable different first-page and odd/even headers, or place the same background in every active variant. Avoid duplicate anchors when applying the layout more than once. The artwork must not displace body text or change the document's intended reading order.

Start with a top margin of 1.35 inches, side margins of 1 inch, and a bottom margin of 1 inch so body content stays above the bottom rule. Put the dynamic footer below that rule, at 0.32 inches from the page bottom in the supplied templates. Adjust footer wrapping within the printable area without moving body text into the logo/rules. These are starting layout values; rendering, not XML settings alone, establishes that the placement is correct.

Use the required current-date/confidentiality/page-number footer from memo-standard.md. Do not copy the reference memo's old dates or footer text. Check every rendered page for the visible logo, correct aspect ratio, rules, text clearance, readable footer and actual page numbers. Preserve the hard six-page maximum. The packaged image and placement instructions alone do not establish that a new memo was rendered or that the runtime has a working renderer.
