---
name: create-tesla-wrap
description: Create and edit Tesla Paint Shop wraps with pixel-exact official template masks, mapped panel orientation, crisp artwork, and validated 1024 × 1024 PNGs strictly under 1 MB. Default to the user's Model Y 2025 Premium.
---

# Create Tesla Wrap 2.0

## Priority and nonnegotiable output

Prioritize official template geometry above all else, then correct physical orientation, then artwork fidelity. Never trade geometry or orientation for appearance or file size. Deliver only a genuine PNG, exactly 1024 × 1024, **strictly below 1,000,000 bytes**. There is no minimum file size. Use a filename stem of 1–30 letters, digits, underscores, hyphens, or spaces.

Use the user's confirmed **Model Y 2025 Premium** by default; do not ask which car again. Only select another template when the user requests another vehicle. The bundled map, assets, and validator apply only to Model Y 2025 Premium; establish a separate official mask, orientation map, and compatible validator for any other vehicle. Never validate another vehicle against this Model Y fingerprint or its 20-panel count.

Official sources:
- Repository: https://github.com/teslamotors/custom-wraps
- Exact template: https://raw.githubusercontent.com/teslamotors/custom-wraps/master/modely-2025-premium/template.png

Keep high-resolution working images, enlarged inspection crops, drafts, mockups, placement maps, and diagnostics internal unless the user asks. Show only the validated final 1024 × 1024 PNG, once, inline (see Section 6).

## 1. Lock and map the template BEFORE making artwork

Read [panel-orientation.md](references/panel-orientation.md), the authoritative source for panel identities, physical orientation, ground-facing edges, door-pair composition, and orientation exceptions. Also read [panel-map.json](references/panel-map.json) for machine-readable geometry and the source fingerprint. Inspect `assets/modely-2025-premium-template.png`; preserve it untouched. Its SHA-256 is pinned in the JSON. The bundled `assets/modely-2025-premium-panel-ids.png` maps all **20** panel islands pixel by pixel, including four individually identified roofline pillars.

Check the official source when available. Compare downloaded bytes with the pinned original. If it changes, do not silently reuse old masks: inspect and update the stored original, panel ID masks, bounds/areas, orientation reference, and SHA-256 fingerprint together; revalidate the complete set against the new official original. Recheck any affected panel count or IDs. Do not accept changed source bytes solely because their fingerprint can be updated. If live access fails, use the pinned copy and disclose that current-source verification was unavailable. Never use a previous wrap, generated silhouette, screenshot, approximation, or bounding rectangle as the geometry authority.

For each panel, extract its original alpha using the ID map. Record ID, exact support bounds/area, physical identity, top/front vectors, intended artwork, baseline anchors/angle, transform, and orientation confidence in an internal placement manifest. Map all panels even when some receive only a flat fill. Follow the orientation reference when recording axes, exceptions, and any combined door-pair placement.

Confirm the planned design fits its intended panel masks before generating the final composition. Clip fills/stripes deliberately; ensure logos/text do not accidentally touch or cross edges. Plan each panel or permitted door pair and document intended continuity across seams. For seam-spanning door artwork, distinguish intentional clipping at the seam from accidental clipping at the combined surface’s outer boundary.

## 2. Place artwork using physical panel axes

Before placing artwork, apply every relevant rule in [panel-orientation.md](references/panel-orientation.md) and inspect [ground-edge-reference.png](references/ground-edge-reference.png). Reading and applying these references is mandatory on every wrap creation or edit; do not rely on remembered orientations.

Use the orientation reference as the single authority for panel axes, measured baselines, combined door designs, ground-facing edge segments, and unresolved orientations. Keep its rules there instead of duplicating them in this file. Record the applied rules and transforms in the placement manifest, then check the artwork against them during the orientation audit.

Preserve approved details on unrelated edits.

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

Run the bundled validator from the skill directory:

```bash
python scripts/check_wrap.py /absolute/path/final.png --template assets/modely-2025-premium-template.png
```

Require PASS. The checker verifies file and geometry constraints, not semantic artwork orientation or 3D appearance. Keep the four audit results internally; never imply all checks passed when any are blocked.

## 5. Preserve fidelity and enforce byte range

PNG compression is lossless: changing compression alone does not change decoded pixels or line sharpness. File size is not a fidelity score; a 500 KB lossless PNG can have exactly the same sharpness and detail as a 900 KB encoding of the same image. Assess fidelity from the actual pixels, source accuracy, and edge quality. First preserve full-resolution color and edge detail and try lossless encoding. If over the cap, remove unnecessary metadata and optimize losslessly before considering minimal color reduction. Never alter original alpha, exact required colors, dimensions, or geometry to fit. If quantizing artwork, preserve alpha separately, avoid boundary dithering, and compare visually before acceptance.

There is no minimum file size. Choose the highest-fidelity compliant export based on actual pixel quality. Never add padding, noise, or unnecessary detail merely to increase file size. A smaller lossless encoding is acceptable when it preserves the same pixels and sharpness.

## 6. Save and deliver

Persist the final artifact using the applicable file-saving workflow, then display the exact saved, validated 1024 × 1024 PNG inline exactly once, followed by a brief confirmation of what changed (plus vehicle and measured byte count). Do not show extra previews, additional files, or separate download links unless the user asks. Deliver no draft, high-resolution working image, enlarged crop, or diagnostic. If image-generation tooling necessarily exposes a draft, do not repeat it or treat it as completion; finish the verified deliverable.
