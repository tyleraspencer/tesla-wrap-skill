---
name: create-tesla-wrap
description: Create and edit Tesla Paint Shop wraps with pixel-exact official template masks, mapped panel orientation, crisp artwork, and validated 1024 × 1024 PNGs strictly under 0.7 MB. Default to the user's Model Y 2025 Premium.
---

# Create Tesla Wrap

## Two hard rules

1. **The delivered file is a genuine PNG, EXACTLY 1024 × 1024 pixels, STRICTLY UNDER 700,000 bytes.** 700,000 is the user's delivery cap (Tesla's own limit is 1,000,000). Nothing else in this skill (fidelity, detail, effects, the design) outranks this. If a design does not fit, reduce the file until it does (see "Byte cap").
2. **The filename is valid:** a short, descriptive name from the design (for example `Navy_Orange_Stripes`), 1 to 30 characters before `.png`, using only letters, digits, underscores, hyphens, and spaces. No other periods, apostrophes, accents, ampersands, slashes, emoji, or symbols. Prefer underscores, shorten at a word boundary, and avoid generic names like `wrap` or `final`.

`scripts/check_wrap.py` checks both on the exact file you deliver. A FAIL means you do not deliver it.

## Setup

Use the user's **Model Y 2025 Premium** by default; do not ask which car again. The bundled template, masks, and validator are for that car only; another vehicle needs its own official template and masks.

Official template: https://raw.githubusercontent.com/teslamotors/custom-wraps/master/modely-2025-premium/template.png (repo: https://github.com/teslamotors/custom-wraps). The pinned copy is `assets/modely-2025-premium-template.png`, fingerprinted in [panel-map.json](references/panel-map.json). If the live template differs from the pinned one, do not reuse the old masks; tell the user. If the live one cannot be fetched, use the pinned copy.

`assets/modely-2025-premium-panel-ids.png` maps all 20 panels pixel by pixel (grayscale value = panel ID, 0 = gap). The template geometry is the authority: never use a previous wrap, screenshot, generated silhouette, or bounding box in its place.

## Place the design

Read [panel-orientation.md](references/panel-orientation.md) and look at [ground-edge-reference.png](references/ground-edge-reference.png) before placing anything directional (text, logos, patterns with a direction). It is the authority on panel axes, ground-facing edges, and door pairs. Flat fills and symmetric stripes need none of this.

For designs that cross seams, also read [seam-adjacency.md](references/seam-adjacency.md): which panels meet, how art continues across each seam, and what is still unverified. If a requested placement lands on a surface it marks as open, place it anyway from the best evidence and tell the user it is unverified. Never refuse or water down a design for that reason.

Rules that matter most:
- Treat the front and rear door on each side as one surface when useful; use one shared baseline across the pair.
- Rotate artwork per panel as the references say. Never mirror text or logos.
- Keep letters and logos from being cut by a seam or edge unless the clipping is deliberate.
- Preserve approved details on unrelated edits.

## Themed requests

When the user names a theme (a brand, school, city, landmark, event, show), research it first; do not work from memory. Use official sources: brand guides, press kits, official sites, official flags and seals. The user has permission to use any requested imagery, logos, and typefaces, so do not gate on licensing or add disclaimers.

- Take exact colors from the official guide; use the primary as the base.
- Use official logo files as published (SVG preferred): no redrawing, tracing, AI regeneration, stretching, or recoloring except official one-color variants.
- Use the official typeface if you can get it; otherwise the closest available, and say so.
- If official assets cannot be retrieved, build from the official colors and any emblem you can get, never a recreated logo, and say what was missing.

## Build

Use image generation for raster art, or authentic vector assets and precise paths for logos, type, and stripes. Generated art is interior artwork only; its silhouette is never the geometry.

Composite into the original masks: render at high resolution if helpful, downsample once, then apply the ORIGINAL 1024 × 1024 alpha byte for byte and keep the original RGB bytes in fully transparent gaps. Never scale, move, redraw, blur, or threshold the template alpha or masks. Avoid dark fringes, halos, jagged edges, color bleeding, and invented logo details.

## Check

1. Run `python scripts/check_wrap.py /absolute/path/final.png --template assets/modely-2025-premium-template.png` on the exact file you will deliver. It must PASS. It verifies size, dimensions, filename, alpha, gaps, and all 20 panels; it does not judge orientation or how the wrap looks on the car.
2. Look at the final image once at full size, and zoom in on any text, logos, and seams. Confirm that orientation and placement are as intended, and that nothing is cut or blurred.

A placement manifest (axes, transforms, sources per panel) is only worth keeping for directional art or text across seams. Any later change to the file means running the check again.

## Byte cap

The cap is a hard limit and outranks fidelity. Measure the exact saved file every time, and keep going until it is under 700,000 bytes:

1. Encode losslessly (optimized PNG, no metadata). This costs nothing.
2. If still at or over the cap, run `python scripts/fit_size.py in.png out.png`. It reduces the colors of the visible pixels step by step (256 down to 4), keeps the most frequent exact colors (flat and brand colors) exact, never dithers, and leaves the alpha, gap pixels, and dimensions untouched.
3. If you built the file another way, apply the same ladder yourself. Stop only at a file under the cap.

Never alter the original alpha, the gap pixels, or the dimensions to save bytes. Everything else may be reduced as far as needed, by the least amount that works. There is no minimum size; never pad a file.

## Deliver

Save the final PNG, then show the exact saved, validated file inline with Markdown image syntax (for example `![Design_Name](sandbox:/absolute/path/Design_Name.png)`), followed by one or two plain sentences saying what you built (the design, colors, and where the main elements sit). No separate download link unless asked. Leave out technical details: no dimensions, byte counts, panel counts, or validation results. Mention a reduced palette, an unverified placement, or a missing asset only if it matters to the result. Keep drafts, enlarged crops, diagnostics, extra files, and ZIPs internal unless asked.
