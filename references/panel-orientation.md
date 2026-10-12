# Model Y 2025 Premium panel orientation

Use this file as the authoritative source for panel identities, physical orientation, ground-facing edges, door-pair composition, and orientation exceptions. Read and apply it before placing artwork on every creation or edit.

Coordinates use canvas origin at upper-left; x right, y down. Bounds are half-open support bounds, including all nonzero-alpha fringe. Bounds are locators, NEVER masks. Canvas-left/right does not establish driver/passenger identity.

The exact pixel ownership map is `assets/modely-2025-premium-panel-ids.png`: grayscale value = panel ID, zero = gap. Obtain each exact panel alpha as `where(ids == ID, original_alpha, 0)`. Never threshold or resample alpha. `panel-map.json` records source fingerprint, bounds, areas, and assignment method.

| ID | Panel | Exact support bounds (x0,y0,x1,y1) | Artwork orientation |
|---|---|---|---|
| 1 | Front bumper | (242, 6, 780, 120) | 180°: artwork top toward canvas bottom; vehicle front toward canvas top. |
| 2 | Hood | (373, 108, 648, 342) | 180°: artwork top toward canvas bottom; vehicle front toward canvas top. |
| 3 | Canvas-left front quarter | (108, 112, 334, 370) | Top inward/right; bottom outward/left. Start 90° clockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 4 | Canvas-right front quarter | (691, 111, 915, 371) | Top inward/left; bottom outward/right. Start 90° counterclockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 5 | Canvas-left long roofline pillar | (339, 344, 391, 814) | Confirmed roofline pillar. Follow individual strip contour for fills/accents. Record readable axes as “not required — user waiver”; do not invent vectors or block completion on pillar axes. |
| 6 | Canvas-right long roofline pillar | (629, 345, 682, 815) | Confirmed roofline pillar. Follow individual strip contour for fills/accents. Record readable axes as “not required — user waiver”; do not invent vectors or block completion on pillar axes. |
| 7 | Canvas-left front door | (80, 345, 262, 598) | Top inward/right; bottom outward/left. Start 90° clockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 8 | Canvas-right front door | (759, 347, 940, 599) | Top inward/left; bottom outward/right. Start 90° counterclockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 9 | Canvas-right mirror cap | (677, 364, 752, 409) | Identity retained from prior skill; exact directional axes unresolved. Require on-car evidence for directional graphics. |
| 10 | Canvas-left mirror cap | (269, 365, 345, 410) | Identity retained from prior skill; exact directional axes unresolved. Require on-car evidence for directional graphics. |
| 11 | Canvas-left rear door | (66, 567, 238, 795) | Top inward/right; bottom outward/left. Start 90° clockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 12 | Canvas-right rear door | (781, 570, 953, 798) | Top inward/left; bottom outward/right. Start 90° counterclockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 13 | Canvas-left rear quarter | (121, 777, 268, 953) | Top inward/right; bottom outward/left. Start 90° clockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 14 | Canvas-right rear quarter | (754, 780, 901, 956) | Top inward/left; bottom outward/right. Start 90° counterclockwise; baseline parallel to the relevant measured local lower border; follow the combined-door exception for spanning artwork. Front toward canvas top. |
| 15 | Canvas-left short roofline pillar | (299, 812, 359, 965) | Confirmed roofline pillar. Follow individual strip contour for fills/accents. Record readable axes as “not required — user waiver”; do not invent vectors or block completion on pillar axes. |
| 16 | Canvas-right short roofline pillar | (664, 813, 722, 967) | Confirmed roofline pillar. Follow individual strip contour for fills/accents. Record readable axes as “not required — user waiver”; do not invent vectors or block completion on pillar axes. |
| 17 | Rear spoiler | (354, 871, 666, 932) | Canvas-upright: top upward, bottom downward; text reads left-to-right. |
| 18 | Canvas-left rear bumper corner | (53, 883, 177, 1017) | User-confirmed: bottom mostly outward/left with a slight downward component; top opposite/inward. The slightly angled outward line is the ground-level bottom edge. Align artwork baseline parallel to that measured edge. |
| 19 | Canvas-right rear bumper corner | (850, 885, 971, 1019) | User-confirmed: bottom mostly outward/right with a slight downward component; top opposite/inward. The slightly angled outward line is the ground-level bottom edge. Align artwork baseline parallel to that measured edge. |
| 20 | Trunk panel | (393, 936, 633, 1017) | Canvas-upright: top upward, bottom downward; text reads left-to-right. |

## Ground-facing edge reference

Inspect [ground-edge-reference.png](ground-edge-reference.png), the user's updated reference with red strokes drawn along the ground-facing edges. Use this clearer edge-marked image in place of the earlier circled reference to identify physical bottom edges and their directions for text/logo alignment. Pair it with the untouched official template: use the red-marked reference for orientation and the original template for exact panel shapes and pixel boundaries. Treat stroke thickness, endpoints, and hand-drawn angles as directional guides, never precise geometry; measure alignment from the corresponding original-template edge. Never trace red strokes into masks or include them in final artwork.

| Panels | Ground-facing segment indicated by the user |
|---|---|
| Front bumper **1** | Upper outer left and right edge portions marked near the top of the canvas. |
| Front quarters **3, 4** | Small outer terminal extensions just above the front doors, around y330–342. This does not make every quarter-panel border ground-facing. |
| Doors **7, 8, 11, 12** | Outer left/right lower edges, considered together per side when designing across doors. |
| Rear bumper corners **18, 19** | Angled outward edges; bottom direction mostly outward and slightly downward. |

The user's marked image supersedes the earlier “only seven panels” classification and blanket quarter-panel exclusion. “Ground” means the physical lower/ground-facing edge, not road contact. Unmarked quarter-panel borders remain local lower borders, not ground-facing references. Measure each marked segment’s actual original-template contour. Do not treat a full door/quarter outline or curved wheel arch as a straight ground baseline, and do not infer a ground-facing edge from a panel’s bounding box.

## Alignment and remaining uncertainty

- The hood, front bumper, side, rear bumper corner bottom edges, spoiler, and trunk orientation rules are user-confirmed. Pillar identities are user-confirmed; the user does not require pillar orientation clarification.
- For independent panel artwork, fit a straight baseline to the appropriate local lower-border segment, excluding wheel arches and rounded corners. For artwork spanning a door pair, fit ONE shared straight baseline to the pair’s bottom edges; this overrides separate per-door angle matching. Never bend a spanning word or rotate its fragments independently. Record fit anchors and angle; nominal ±90° rotation is insufficient.
- Treat the front and rear doors on each side as one combined design surface when useful for designs, text, logos, or stripes: canvas-left IDs 7 + 11; canvas-right IDs 8 + 12. A design may span the door seam; it need not fit inside one door. Plan the composition across the pair, then clip/export through the two original masks, preserving each door’s exact geometry and the transparent gap. Do not combine opposite sides into one surface.
- For art spanning doors, record one shared artwork orientation/baseline, fit anchors and angle, any placement offsets into the two immutable masks, seam spacing, letter spacing across the gap, height, and seam endpoints. Check intended on-car seam continuity; an atlas-only fit does not establish 3D continuity, and atlas gaps may not represent on-car spacing.
- Rotate artwork independently on either side. Never mirror text, asymmetric logos, or geographic outlines. Artwork top and forward-facing direction are separate axes.
- Rear spoiler canvas orientation is confirmed; which pixels cover its physical upper surface versus underside remains unresolved. Do not infer that split from canvas top/bottom.
- The four pillar masks are exact in 2D. Follow each contour for fills and accents; do not ask for pillar orientation or hold up a wrap because those readable axes are unspecified. Do not invent A/B/C/D pillar names or claim 3D axes were verified.
- On both rear bumper corners, the slightly angled outward line represents a bottom edge that is flat with the ground on the vehicle. Measure its local angle from the original mask, separately for left and right; orient artwork top opposite the outward-and-slightly-downward bottom vector and align its baseline with that edge. Do not mirror text or infer a numerical angle from the verbal description.
- A 2D mask cannot prove 3D appearance, seam correspondence, or upright presentation. State the limits of verification honestly. For unresolved panels other than the waived pillar orientation, use nondirectional fills/accents or ask a focused question before directional placement.
- For nondirectional fills, mark unknown axes as “not needed for this artwork.” Resolve uncertainty only when it affects requested directional artwork; never guess an orientation. For pillars, record readable axes as “not required — user waiver.”
