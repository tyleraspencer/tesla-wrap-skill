# Model Y 2025 Premium seam adjacency (on-car evidence)

Source: Tesla app 3D preview of a position-coded calibration wrap (R = canvas x, G = canvas y, grid every 32 px, panel ID + canvas-up arrow on every panel). Photos taken: front-left three-quarter (2), front-left low, rear-left three-quarter, and straight top-down. Passenger-side panels (4, 8, 12, 14, 19, 6, 16, 9) are confirmed only where the top-down view shows them; the rest is inferred from the template's left/right symmetry.

Confidence: **seen** = visible in a photo; **inferred** = follows from seen facts plus template geometry; **open** = not established. Pair this file with [panel-orientation.md](panel-orientation.md); where they disagree, the on-car evidence here wins for adjacency and continuity, and `panel-orientation.md` still wins for geometry and ground-edge baselines.

## Global findings

- **Canvas-left is the car's left (driver) side.** Seen in the top-down view with the nose up: 3, 13, 10 sit on the left, 4, 14, 9 on the right. Not mirrored; canvas x increases toward the car's right on the hood.
- **Canvas-up points toward the front of the car** on the hood (2), front quarters (3, 4), doors (7, 11), rear quarter (13) and the pillars' fills. Seen on the hood from above and on 3, 7, 11, 13 from the side.
- **Rear bumper corner 18:** canvas-up points toward the front and slightly up, along the side of the car; the label reads rotated about 90°. Seen. Consistent with `panel-orientation.md`.
- **Trunk 20** is canvas-upright when viewed from behind the car; its text reads left to right. Seen.
- **Spoiler 17** wraps over the top of the spoiler and onto its rear lip. Top-down view: canvas-up points toward the front on the top surface, and the heavy y = 896 grid line sits on the trailing edge. So roughly canvas y 871–896 is the top surface and y 896–932 is the rear lip. Seen, approximate; do not place text across that line.
- **Mirror cap 10:** the label reads upside down from the side with its arrow at the bottom, so canvas-up points toward the ground on the cap's outer face. Seen on two photos; the cap's other faces were not photographed. Treat directional art on mirror caps as unverified.

## Seams

| Seam | Where on the car | Continuity | Confidence |
|---|---|---|---|
| 7 \| 11 | Front/rear door shut line | Grid lines continue across; one shared baseline works | seen |
| 11 \| 13 | Rear door to rear quarter (behind rear door) | Continues in canvas y; color gradient is smooth across | seen |
| 3 \| 7 | Front fender to front door (behind the front wheel arch) | Continues; fender's lower canvas edge meets door's top edge | seen |
| 3 \| 2 | Fender top to hood side edge | Hood's canvas-left edge meets fender's inner edge | seen |
| 2 \| 1 | Hood front edge to bumper top | Hood canvas-top edge meets bumper canvas-bottom edge; bumper canvas-top is the low/ground side | inferred (matches `panel-orientation.md` ground-edge note) |
| 1 \| 3 | Bumper side end to front fender at the wheel arch | Bumper wraps the front corner and ends near the front of the wheel arch | seen |
| 5 → 15 | Roof rail to the rear-glass side pillar | One continuous strip: 5's lower end flows into 15's upper end, color shifts green to cyan at the C-pillar | seen |
| 15 \| 17 | Rear-glass side pillar to spoiler | 15 ends at the spoiler's side | seen |
| 13 \| 18 | Rear quarter to rear bumper corner (below the tail lamp) | Horizontal seam; 18 sits below it | seen |
| 18 \| 20 | Rear bumper corner to trunk face | Vertical seam at the tail-lamp edge; 18 wraps from the side onto the rear face's lower corner | seen |
| 17 \| 20 | Spoiler lip to trunk face | The tail-lamp bar sits between them on the car; they do not touch | seen |
| 10 → 3/7 | Mirror cap to the fender/door corner | Cap is a separate surface; no continuity | seen |

Passenger-side equivalents (4 \| 8, 8 \| 12, 12 \| 14, 4 \| 2, 4 \| 1, 6 → 16, 16 \| 17, 14 \| 19, 19 \| 20, 9) are **inferred** by symmetry.

## How to use this when planning a multi-panel design

1. Spanning art is safe across 7 + 11 (and 8 + 12), and across 11 + 13 and 3 + 7 when fitting to the shared outer baseline.
2. Roof pillars: continue a stripe from 5 into 15 in one stroke; do not restart it.
3. A stripe from the hood down the nose should run 2 → 1; place it using the hood's canvas-top edge and the bumper's canvas-bottom edge.
4. Avoid text, logos, or directional art on: mirror caps (9, 10), the spoiler across y = 896, and any passenger-side panel until photographed.
5. The rear face is 20 (center) with 18/19 wrapping the lower corners, and 13/14 above them on the sides. Keep logos inside 20.

## Still open

- Passenger-side photos, a straight-on front, a straight-on rear, and close-ups of the front fender and bumper corner to confirm 1 | 3 precisely.
- Mirror cap faces other than the outer one.
- The exact canvas pixel where each seam's art lines up, since the photos show correspondence by eye, not by sampled pixel values.
