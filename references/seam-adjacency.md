# Model Y 2025 Premium seam adjacency (on-car evidence)

Source: Tesla app 3D preview of a position-coded calibration wrap (R = canvas x, G = canvas y, grid every 32 px, heavy line every 128 px, panel ID + canvas-up arrow on every panel). Views reviewed: front-left three-quarter (two), rear-left three-quarter, top-down, straight-on front, straight-on rear, rear-right three-quarter, front-right three-quarter, and a passenger-side profile. The first four are stored in [calibration-photos/](calibration-photos/README.md); the rest were reviewed but not stored because they show the in-car screen.

Confidence: **seen** = visible in a photo; **inferred** = follows from seen facts plus template geometry; **open** = not established. Pair this file with [panel-orientation.md](panel-orientation.md); where they disagree on adjacency or continuity, this file wins, and `panel-orientation.md` still wins for geometry and ground-edge baselines.

## Global findings

- **Canvas-left is the car's left (driver) side; canvas-right is the right (passenger) side.** Seen from above (nose up), from the front, and from behind. Nothing is mirrored; text on the hood and trunk reads left-to-right in canvas order.
- **Canvas-up points toward the front of the car** on the hood (2), front quarters (3, 4), doors (7, 8, 11, 12), rear quarters (13, 14) and rear bumper corners (18, 19). Seen on both sides.
- **Bumper 1:** canvas-up points toward the ground. The label's arrow points down on the car, so the canvas-top edge is the low edge and the canvas-bottom edge is the one that meets the hood. Seen from the front, from both sides.
- **Hood 2:** canvas-up points toward the front; the label reads upside down to someone standing at the nose.
- **Trunk 20** is canvas-upright when viewed from behind; text reads left to right. Seen.
- **Mirror caps 9 and 10:** both labels read upside down from the side with the arrow at the bottom, so canvas-up points toward the ground on the outer face. Seen on both caps. The other faces of the caps were not photographed.
- **Spoiler 17:** the label and the y = 896 line sit on the thin top strip just under the rear glass, near the crest. Below the crest, the rear-facing lip shows only vertical grid lines. Roughly canvas y 871–896 is the top strip and 896–932 is the lip, but the split is approximate and the strip is very thin. Do not put text or logos on the spoiler.

## Seams

| Seam | Where on the car | Continuity | Confidence |
|---|---|---|---|
| 7 \| 11, 8 \| 12 | Front/rear door shut lines | Grid lines continue across; one shared baseline works | seen |
| 11 \| 13, 12 \| 14 | Rear door to rear quarter (behind the rear door) | Continues in canvas y; color is smooth across | seen |
| 3 \| 7, 4 \| 8 | Front fender to front door | Fender's lower canvas edge meets the door's top edge | seen |
| 3 \| 2, 4 \| 2 | Fender to hood | Diagonal seam from the windshield base down to the inner end of the headlight; the hood's side edges meet the fenders' inner edges | seen |
| 2 \| 1 | Hood front edge to bumper top | Along the chrome strip across the nose; hood canvas-top edge meets bumper canvas-bottom edge | seen |
| 3 \| 1, 4 \| 1 | Fender front tip to bumper corner | Along the headlight strip and around the front corner; the fender's front tip sits above the headlight, the bumper below it | seen |
| 5 → 15, 6 → 16 | Roof rail to the rear-glass side pillar | One continuous strip: the long pillar flows into the short one; color shifts green to cyan at the C-pillar | seen |
| 15 \| 17, 16 \| 17 | Rear-glass side pillar to spoiler | Pillar ends at the spoiler's side | seen |
| 13 \| 18, 14 \| 19 | Rear quarter to rear bumper corner (below the tail lamp) | Horizontal seam; the corner piece sits below it | seen |
| 18 \| 20, 19 \| 20 | Rear bumper corner to trunk face | Slanted seam running from the tail-lamp bar down to the bumper; the corner piece wraps from the side onto the rear face | seen |
| 17 \| 20 | Spoiler lip to trunk face | The tail-lamp bar sits between them on the car; they do not touch | seen |
| 9 → 4/8, 10 → 3/7 | Mirror cap to the fender/door corner | Cap is a separate surface; no continuity | seen |
| 13 \| 20, 14 \| 20 | Rear quarter to trunk face, above the corner pieces | The quarter may wrap slightly onto the rear face beside the tail lamp | open |

## How to use this when planning a multi-panel design

1. Spanning art is safe across 7 + 11 and 8 + 12, and across 11 + 13, 12 + 14, 3 + 7 and 4 + 8 when fitted to the shared outer baseline.
2. Roof pillars: continue a stripe from 5 into 15 (and 6 into 16) in one stroke; do not restart it.
3. A stripe from the hood down the nose runs 2 → 1 across the chrome strip: use the hood's canvas-top edge and the bumper's canvas-bottom edge. A stripe across the nose corner crosses the headlight strip from the fender (3 or 4) into the bumper.
4. Remember bumper 1 is upside down relative to the hood: canvas-up on the bumper is toward the ground, canvas-up on the hood is toward the nose.
5. Avoid text, logos, or directional art on the mirror caps (9, 10) and on the spoiler (17).
6. The rear face is 20 (center) with 18 and 19 wrapping the lower corners; keep logos inside 20.

## Still open

- Mirror cap faces other than the outer one.
- Whether 13 and 14 wrap onto the rear face beside the tail lamp.
- The exact canvas split between the spoiler's top strip and its lip.
- The exact canvas pixel where each seam's art lines up. The photos show correspondence by eye, not by sampled pixel values.
