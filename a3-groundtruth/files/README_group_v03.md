# ett3 A3 Ground Truth · group packet · README v03

Pin-up Fri Oct 30 2026, 12 pm. 9 sheets, all 11 x 17 landscape. New in v03: sheet 08 S2 Splat atlas (Gaussian splat shots).

## Which file to open
- **Review:** `ett3-A3_packet_review_v03.pdf` (every open slot boxed and numbered, slot list at the end). Mark up in Acrobat or Preview. `ett3-A3_packet_v03.pdf` is the clean print set.
- **Draw:** `ai/ett3-A3_<sheet>_vNN.ai`, one per sheet (cover v06, sheet 08 v01, the others v05), or `ai/ett3-A3_packet_v06.ai` (all 9 artboards). Rasters are linked from `links/`.
- **Lay out:** `indd/ett3-A3_packet_v05.indd` (InDesign 2026) or `indd/ett3-A3_packet_v05.idml` (any recent InDesign). Each page places the sheet's `.ai`; your text goes on layer `group-edit` (styles A3-head, A3-body, A3-note, A3-proxy).
- Keep the `indd/` folder together: the `.indd` links to `indd/Links/`. If InDesign or the IDML asks for links, point it at `indd/Links/`.

## Fonts
Public Sans (OFL). Mac: double-click each OTF in `fonts/` > Font Book > Install. PC: right-click > Install. InDesign also picks them up from `indd/Document fonts/`.

## Editing rules
- Work on a copy. Put your initials and a version in the name: `ett3-A3_04_D3b-plant-drawings_v05_MK.ai`.
- Never edit layers `underlay` or `plan` (locked). Draw on `annot-field`.
- Scans of hand drawings: 300 ppi, place on `annot-field` inside the frame.

## Swap in field data
Copy `01_src/ett3-A3_field-data_PROXY_v01.csv` to `01_src/ett3-A3_field-data_v01.csv`, type the field values, and change `source` from `proxy` to `field` on each row you replace. Send it back to the group; the build is re-run and every P mark on that value disappears.

## Open slots (numbers match the review PDF)
| Sheet | What | FIELD | DATA | CONFIRM | P |
|---|---|---|---|---|---|
| 00 Cover | names, date, group to-dos | 7 | 0 | 0 | 3 |
| 01 D1 | group's Part A map, key, field notes | 3 | 0 | 0 | 0 |
| 02 D2 | patch outlines, north, KML trace | 3 | 0 | 5 | 15 |
| 03 D3 | plot features, legacy plant, plot radius, P values | 4 | 0 | 6 | 95 |
| 04 D3b | 3 plant drawings, captions, drawn by | 6 | 0 | 3 | 6 |
| 05 D3c | 4 hand sections: name, s from / to | 8 | 0 | 0 | 0 |
| 06 S1 | north on scan | 0 | 0 | 5 | 0 |
| 07 Data | station table | 0 | 1 | 0 | 93 |
| 08 S2 | splat atlas (no slots) | 0 | 0 | 0 | 0 |
| total | 263 slots | 31 | 1 | 19 | 212 |
