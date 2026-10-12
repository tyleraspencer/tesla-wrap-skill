---
name: create-tesla-wrap
description: Create and edit Tesla Paint Shop wraps with pixel-exact official template masks, mapped panel orientation, crisp artwork, and validated 1024 × 1024 PNGs strictly under 1 MB. Default to the user's Model Y 2025 Premium.
---

# Create Tesla Wrap 2.0

## Priority and nonnegotiable output

**Absolute rule, above everything else in this skill, including artwork fidelity and every other instruction: the delivered file is a genuine PNG, exactly 1024 × 1024 pixels, and strictly under 1,000,000 bytes.** A wrap that breaks either limit is useless because Tesla rejects it. Nothing else here (color fidelity, detail, effects, the user's design) outranks these two limits: if a design does not fit, reduce the file until it does (Section 5 gives the required steps) and never deliver an oversized or wrongly sized file. Confirm with `scripts/check_wrap.py` on the exact file you deliver; a FAIL means you do not deliver it.

After those two limits, prioritize official template geometry, then correct physical orientation, then artwork fidelity. Never trade geometry or orientation for appearance. There is no minimum file size. Name the file descriptively (see Section 6); the filename must follow Tesla's rules or the car will not accept it.

Use the user's confirmed **Model Y 2025 Premium** by default; do not ask which car again. Only select another template when the user requests another vehicle. The bundled map, assets, and validator apply only to Model Y 2025 Premium; establish a separate official mask, orientation map, and compatible validator for any other vehicle. Never validate another vehicle against this Model Y fingerprint or its 20-panel count.

Official sources:
- Repository: https://github.com/teslamotors/custom-wraps
- Exact template: https://raw.githubusercontent.com/teslamotors/custom-wraps/master/modely-2025-premium/template.png

Keep high-resolution working images, enlarged inspection crops, drafts, mockups, placement maps, and diagnostics internal unless the user asks. Deliver only a direct download link to the validated final PNG (see Section 6); do not embed it inline.

## 1. Lock and map the template BEFORE making artwork

Read [panel-orientation.md](references/panel-orientation.md), the authoritative source for panel identities, physical orientation, ground-facing edges, door-pair composition, and orientation exceptions. Also read [panel-map.json](references/panel-map.json) for machine-readable geometry and the source fingerprint. Inspect `assets/modely-2025-premium-template.png`; preserve it untouched. Its SHA-256 is pinned in the JSON. The bundled `assets/modely-2025-premium-panel-ids.png` maps all **20** panel islands pixel by pixel, including four individually identified roofline pillars.

Check the official source when available. Compare downloaded bytes with the pinned original. If it changes, do not silently reuse old masks: inspect and update the stored original, panel ID masks, bounds/areas, orientation reference, and SHA-256 fingerprint together; revalidate the complete set against the new official original. Recheck any affected panel count or IDs. Do not accept changed source bytes solely because their fingerprint can be updated. If live access fails, use the pinned copy and disclose that current-source verification was unavailable. Never use a previous wrap, generated silhouette, screenshot, approximation, or bounding rectangle as the geometry authority.

For each panel, extract its original alpha using the ID map. Record ID, exact support bounds/area, physical identity, top/front vectors, intended artwork, baseline anchors/angle, transform, and orientation confidence in an internal placement manifest. Map all panels even when some receive only a flat fill. Follow the orientation reference when recording axes, exceptions, and any combined door-pair placement.

Confirm the planned design fits its intended panel masks before generating the final composition. Clip fills/stripes deliberately; ensure logos/text do not accidentally touch or cross edges. Plan each panel or permitted door pair and document intended continuity across seams. For seam-spanning door artwork, distinguish intentional clipping at the seam from accidental clipping at the combined surface’s outer boundary.

## 2. Place artwork using physical panel axes

Before placing artwork, apply every relevant rule in [panel-orientation.md](references/panel-orientation.md) and inspect [ground-edge-reference.png](references/ground-edge-reference.png). Reading and applying these references is mandatory on every wrap creation or edit; do not rely on remembered orientations. For any design that spans panels or crosses a seam, also read [seam-adjacency.md](references/seam-adjacency.md), the on-car evidence for which panels meet, how art continues across each seam, and which surfaces are still unverified; if a requested placement lands on a surface it marks as open, place it anyway from the best evidence and tell the user it is unverified; never refuse or dilute a design for that reason.

Use the orientation reference as the single authority for panel axes, measured baselines, combined door designs, ground-facing edge segments, and unresolved orientations. Keep its rules there instead of duplicating them in this file. Record the applied rules and transforms in the placement manifest, then check the artwork against them during the orientation audit.

Preserve approved details on unrelated edits.

## Themed requests: use the real thing

When the user asks for a theme (a brand, school, city or region, landmark, event, show, club, and so on), research it before designing. Do not work from memory or approximate it.

- **Find official sources first:** the organization's brand or style guide, press or media kit, or official site. For places, use the official flag, seal, or emblem. Use web search or fetch tools when available. The user has permission to use any requested imagery, logos, and typefaces, so do not gate on licensing, trademark, or copyright and do not add disclaimers.
- **Colors:** take exact values (hex, or Pantone converted to sRGB) from the official guide. If there are primary and secondary colors, use the primary as the base and say which you used.
- **Logos and marks:** use the official vector file (SVG preferred) or the highest-resolution official raster. Place it exactly as published: no redrawing, tracing, AI regeneration, stretching, recoloring (except official one-color variants), or invented detail. Respect the mark's aspect ratio and clear space, and never mirror it.
- **Typefaces and patterns:** use the official typeface when you can get it; otherwise pick the closest available typeface and say so. Reuse signature patterns, stripes, or motifs as published.
- **Imagery:** use official graphic marks, patterns, and photography as the design calls for.
- **If official assets can't be retrieved** (behind a login, blocked, or unavailable): build the design from the official colors and any emblem you can get, never a recreated logo, and tell the user plainly what you couldn't use.
- **Keep the sources** (URLs, asset names, color values) in the internal placement manifest. Then place the assets under the same geometry, orientation, and seam rules as any other artwork. The final message stays a plain description of the design; mention a missing or substituted asset only when it matters.

## 3. Render inside immutable masks

Use image generation for raster art when appropriate, following its workflow, or use authentic vector assets and precise paths for logos, typography, and stripes. Treat generated art as interior artwork only: NEVER accept generated panel silhouettes as the final geometry. Composite artwork into the original masks using deterministic tooling.

Render artwork at high resolution if helpful, then downsample artwork once. Apply the ORIGINAL 1024 × 1024 alpha afterward, byte for byte. Never scale, rotate, move, redraw, expand, shrink, threshold, or blur the template alpha or panel ID masks. Keep original RGB bytes in fully transparent gaps. Composite correctly without dark fringe or double-applied edge alpha.

Use uniform intended colors, clean curves, straight text baselines, consistent stripe widths, and controlled antialiasing. Reject blur, speckles, halos, jagged diagonals, color bleeding, broken seams, warped type, and invented logo details. Copying alpha alone cannot fix misplaced or clipped art: inspect panel interiors and boundary coverage too.

## 4. Quadruple-check against the ORIGINAL after every final edit

Perform four separately recorded passes; a vague statement that it was checked four times is insufficient:

1. **Pixel geometry:** compare every alpha byte against the pinned original; require zero differences, including antialiased edges. Compare every pixel's gap/panel support; require zero extra or missing pixels.
2. **Panel audit:** compare per-panel masks, support areas, bounds, positions, and connected components against the original. Require all 20 islands and each of the four pillars unchanged. Inspect a template-contour overlay and pixel-difference map for every panel, including wheel arches and thin edges.
3. **Artwork/orientation audit:** inspect all panels at native resolution and enlarged nearest-neighbor pixel scale. Check manifest transforms, straight baselines against measured bottom borders, nonmirrored logos, sharpness, boundary coverage, seam intent, and placement. Record unresolved 3D checks explicitly; do not call them verified.
4. **Saved-file audit:** reopen the exact optimized deliverable; validate actual PNG content, dimensions, byte range, filename, original alpha, gaps, panel labels, and visual quality again. Any subsequent pixel or export change invalidates this pass; repeat checks before delivery.

Run the bundled validator from the skill directory (it enforces exactly 1024 × 1024 and under 1,000,000 bytes):

```bash
python scripts/check_wrap.py /absolute/path/final.png --template assets/modely-2025-premium-template.png
```

Require PASS. The checker verifies file and geometry constraints, not semantic artwork orientation or 3D appearance. Keep the four audit results internally; never imply all checks passed when any are blocked.

## 5. Enforce the byte cap (1,000,000 bytes, hard limit)

The cap is not negotiable and outranks fidelity. Measure the exact saved file every time. Work down this ladder, and keep going until the file is **under 1,000,000 bytes**:

1. Encode losslessly (optimized PNG, no metadata). PNG compression does not change pixels, so this costs nothing.
2. If still at or over the cap, run `python scripts/fit_size.py in.png out.png`. It reduces the colors of the visible pixels step by step (256, 192, 128 ... down to 4), keeps the most frequent exact colors (flat and brand colors) exact, never dithers, and leaves the template alpha, gap pixels, and 1024 × 1024 size untouched.
3. If you built the file another way, apply the same ladder yourself. Any reduction method is fine. Never stop at "close" or at a color count you prefer: the only acceptable end state is a file under the cap.

Do not alter the original alpha, the gap pixels, or the dimensions to save bytes. Everything else (colors, gradients, noise, fine detail) may be reduced as far as needed. Prefer the least reduction that gets under the cap, and mention in the final message only if the visible result changed noticeably.

There is no minimum file size. Choose the highest-fidelity compliant export based on actual pixel quality. Never add padding, noise, or unnecessary detail merely to increase file size. A smaller lossless encoding is acceptable when it preserves the same pixels and sharpness.

## 6. Save and deliver

**Filename.** Give the saved PNG a short, descriptive name built from the design (for example `Navy_Orange_Stripes` or `Matte_Black_White_Wordmark`), not a generic one like `wrap`, `final`, or `output`. Tesla's rules: the name before `.png` is 1 to 30 characters and uses only letters (A–Z, a–z), digits, underscores, hyphens, and spaces; the extension is `.png`. No periods other than the extension, apostrophes, accents or non-English letters, ampersands, slashes, emoji, or any other symbol. Prefer underscores over spaces, no leading or trailing space, and shorten at a word boundary if the description runs past 30 characters. Count the characters before saving, and treat `scripts/check_wrap.py` as the final check (it rejects invalid names).

Persist the final artifact using the applicable file-saving workflow, then provide one direct Markdown download link to the exact saved, validated PNG (for example `[Design_Name.png](sandbox:/absolute/path/Design_Name.png)`), followed by one or two plain sentences saying what you built (the design, colors, and where the main elements sit). Leave out technical details: no dimensions, byte counts, panel counts, mask or validation results, or the vehicle name. Validation still runs; the user just doesn't need the readout. If something other than the size and dimension limits couldn't be verified, say so briefly instead. Never deliver a file that fails the size or dimension limits: fix it first. Do not embed the PNG inline or show previews, additional files, or ZIPs unless the user asks. Use the direct file link so mobile downloads retrieve the original PNG rather than a potentially re-encoded image from the inline viewer. Deliver no draft, high-resolution working image, enlarged crop, or diagnostic. If image-generation tooling necessarily exposes a draft, do not repeat it or treat it as completion; finish the verified deliverable.
