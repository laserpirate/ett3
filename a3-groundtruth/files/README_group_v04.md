# ett3 A3 Ground Truth · group packet · README v04

Pin-up Fri Oct 30 2026, 12 pm. 9 sheets, all 11 x 17 landscape. New in v04: D2 v04 is a site plan on the gaussian splat (two options), D3 v04 has the section on the splat side view and a plant table per zone.

## D2 options
- **Option A (default, in the packet):** site plan of the whole scan footprint at 1:40, splat over the mesh top view, contours 0.25 ft (index 1 ft).
- **Option B (alternate):** detail plan at the fallen log, 1:10, with an inset of option A. It is in `ett3-A3_packet_v04_altB.pdf` (same packet, D2 swapped) and `ai/ett3-A3_02_D2-patch-map-optB_v01.ai`.
- To swap B in for the print set: print the altB PDF, or in InDesign relink page 3 to the option B `.ai`.

## Which file to open
- **Review:** `ett3-A3_packet_review_v04.pdf` (every open slot boxed and numbered, slot list at the end). `ett3-A3_packet_v04.pdf` is the clean print set.
- **Draw:** `ai/ett3-A3_<sheet>_vNN.ai`, one per sheet (cover v07, D2 v06, D3 v06, sheet 08 v01, the others v05), or `ai/ett3-A3_packet_v07.ai` (all 9 artboards). Rasters are linked from `links/`.
- **Lay out:** `indd/ett3-A3_packet_v06.indd` (InDesign 2026) or `indd/ett3-A3_packet_v06.idml`. Each page places the sheet's `.ai`; your text goes on layer `group-edit` (styles A3-head, A3-body, A3-note, A3-proxy).
- Keep the `indd/` folder together: the `.indd` links to `indd/Links/`.

## Fonts
Public Sans (OFL). Mac: double-click each OTF in `fonts/` > Font Book > Install. PC: right-click > Install. InDesign also picks them up from `indd/Document fonts/`.

## Editing rules
- Work on a copy. Put your initials and a version in the name: `ett3-A3_04_D3b-plant-drawings_v05_MK.ai`.
- Never edit layers `underlay` or `plan` (locked). Draw on `annot-field`.
- Scans of hand drawings: 300 ppi, place on `annot-field` inside the frame.

## Swap in field data
Copy `01_src/ett3-A3_field-data_PROXY_v01.csv` to `01_src/ett3-A3_field-data_v01.csv`, type the field values, and change `source` from `proxy` to `field` on each row you replace. Send it back to the group; the build is re-run and every P mark on that value disappears.

## Plant IDs on the Site Photos page
All are tentative (from keyframes, not checked in the field). The list is in the lane QUESTIONS file; please confirm or correct.

## Open slots (numbers match the review PDF)
| Sheet | What | FIELD | DATA | CONFIRM | P |
|---|---|---|---|---|---|
| 00 Cover | names, date, group to-dos | 7 | 0 | 0 | 3 |
| 01 D1 | group's Part A map, key, field notes | 3 | 0 | 0 | 0 |
| 02 D2 | patch outlines, north, upland edge | 1 | 0 | 1 | 3 |
| 03 D3 | water level, plot radius, s 0 bearing, P values | 0 | 0 | 5 | 53 |
| 04 D3b | 3 plant drawings, captions, drawn by | 6 | 0 | 3 | 6 |
| 05 D3c | 4 hand sections: name, s from / to | 8 | 0 | 0 | 0 |
| 06 S1 | north on scan | 0 | 0 | 5 | 0 |
| 07 Data | station table | 0 | 1 | 0 | 93 |
| 08 S2 | splat atlas (no slots) | 0 | 0 | 0 | 0 |
| total | 198 slots | 25 | 1 | 14 | 158 |
