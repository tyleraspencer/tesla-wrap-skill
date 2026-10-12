# Reusable wrap renderer

Read the orientation and seam references first. Use `scripts/render_wrap.py` for deterministic artwork placement and immutable-mask export instead of rewriting compositing code. Dependencies: Pillow, NumPy, and SciPy (for the existing validator).

```bash
python scripts/render_wrap.py references/render-examples/usa.json /absolute/work/USA.png --manifest /absolute/work/placement.json
```

Copy the example to a working design file; replace the palette, layers, asset paths, and panel notes. Every `font` can be one path or a list of fallbacks; the first that exists is used and recorded in the manifest as `fonts_used`. The example lists DejaVu Sans Bold (Linux) then Arial Bold (macOS, Windows); add your own path first to use a different typeface. This is original USA typography, not an official national typeface. Resolve relative image/font paths against the design file's directory. Keep working files and outputs outside the skill directory.

## Design format

Use JSON `version: 1`, `base` (literal color or palette key), `colors` (named colors), `sources` (asset/color provenance), `panel_notes` (string IDs `1` through `20`), and ordered `layers`. Record artwork, physical axes, confidence, and seam intent for every panel in `panel_notes`, including flat fills. All panels start with the base color.

Each layer specifies `panels`, optional `space`, and `operations`. Later layers paint over earlier ones. A shared layer is rendered through each panel's original mask; it never joins or changes masks. Decorative stripes may intentionally reach boundaries; inspect text and logos for outer-boundary clearance.

| Space | Coordinates and orientation |
| --- | --- |
| `atlas` (default) | Original 1024-square canvas coordinates. Text/images use explicit `angle` in Pillow degrees: positive counterclockwise. Apply the orientation reference yourself; zero is not automatically correct. |
| `door_left` | `u` = canvas y, front toward rear; `v` = inset inward from the fitted outer door edge. Restricted to IDs 3, 7, 11, 13. |
| `door_right` | Same `u` and `v` meaning on the right; restricted to IDs 4, 8, 12, 14. |

Both door spaces fit one straight baseline to original door contours at y380–689, excluding the rear wheel arch. Text/images rotate onto that shared baseline without mirroring. Use the door frame for artwork spanning a door pair; this frame is an approximation for neighboring quarter panels and must be checked against their relevant local edges before independent directional placement. `angle` in door space adds a rotation to the fitted baseline. This renderer does not provide an on-car UV projection or automatically solve quarter/bumper baseline angles.

| Operation `kind` | Required fields |
| --- | --- |
| `fill` | `color` |
| `rect` | `box: [x0,y0,x1,y1]`, `color` |
| `polygon` | `points: [[x,y],...]`, `color` |
| `line` | `points`, `width`, `color` |
| `stars` | `centers: [[x,y],...]`, `radius`; optional `color`, `angle` (0 = atlas upright) |
| `text` | `text`, `font`, `font_size`, `center`, `size: [width,height]`; optional `color`, `angle` |
| `image` | `file`, `center`, `size`; optional `angle` |
| `wordmark` | `text`, `font`; optional `cap_height` (default 58), `inset` (default 64, px in from the outer door edge), `min_gap` (default 16), `color`. Door space only, on a layer targeting exactly `[7, 11]` or `[8, 12]` |

Positions and sizes use native canvas pixels even though artwork renders at 4× by default (`--scale 1` through `8`). Text and images fit inside the size box while preserving aspect ratio. Images retain source colors and opacity; rasterize official SVGs accurately before passing them to this Pillow renderer. Never use the decorative primitives to recreate official logos.

**Placement check.** Every `text`, `image`, and `wordmark` is tested before export: its ink, plus a 3 px margin, must stay inside the layer's panels. Anything that crosses a seam or panel edge fails the render with the overshoot in pixels. Set `"allow_clip": true` on that operation when clipping is deliberate. Fills, stripes, stars, and other decorative shapes are never checked and may run to any edge.

**Wordmark.** On a door pair it sets the word on the shared baseline, rotated per side and never mirrored, then sizes the letter gaps so the door seam falls inside one gap and no letter is cut. It tries each gap position, most balanced first, and keeps the first that clears the masks; the choice goes in the manifest under `wordmarks`. The cost is wide, even letter spacing (at least about 16 px, usually 20–24) and a single line of text. Use `text` with `allow_clip` instead for art that should deliberately run across the seam.

The renderer rejects directional marks (text, images, stars, wordmarks) on mirrors and spoiler. Pillars should receive fills/accents only. For atlas placement on all other panels, reading and applying the reference remains mandatory.

## Export and inspection

The renderer verifies the pinned template, all ID areas/bounds, and gap support; renders each layer stack at high resolution; downsamples its artwork once; then copies original alpha and fully transparent RGB unchanged. It saves losslessly, reopens and compares decoded pixels, and runs `check_wrap.py`. It fails rather than silently quantize an oversized export.

The required `--manifest` records every panel, layer, explicit transform parameters, fitted door baselines, provenance, and automated checks. Artwork/orientation remains **PENDING** until native and enlarged visual inspection, contour-overlay inspection, and the skill's full four-pass audit are completed. Keep diagnostics internal. Never interpret validator PASS as proof of semantic orientation, boundary clearance, exact seam continuity, or 3D appearance. Check the live official template separately as required by SKILL.md.

## Tests

Run the regression tests directly (not through `unittest discover`, which cannot import this folder):

```bash
python scripts/tests/test_render_wrap.py
```
