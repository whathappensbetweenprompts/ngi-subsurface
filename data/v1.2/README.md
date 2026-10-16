# Dataset v1.2: the New Mexico side of the basin

*16 October 2026 - Gale*

v1 and v1.1 covered the Texas Permian. v1.2 adds the seven Subpart RR storage sites on the New Mexico side, all in Lea and Eddy counties. As in Texas, I took each site's EPA-approved monitoring plan, pulled out the wells it lists by API number, and joined them to the state's well records. In New Mexico those records come from the Oil Conservation Division (OCD), not the Railroad Commission. The approach follows `../v1/README.md`; this note covers what is new or different.

## Sites

| Site | Operator (per plan) | What the plan lists | Listed wells |
|---|---|---|---|
| Hobbs Field | Oxy | Every well in the Hobbs units, with type and status, as of August 2016 | 714 |
| Titan Treating Facility | Northwind Midstream Partners | Area of review oil and gas well list for Salt Creek AGI No. 2 and No. 3 | 155 |
| Maljamar Gas Plant | Frontier Field Services | Wells in the monitoring area of Maljamar AGI #1 and #2, and wells within 1 mile of the Metropolis well (both tables are images; see OCR below) | 193 |
| Copperhead Gas Plant | Targa Midstream Services | Oil and gas wells in the maximum monitoring area, with a risk rating | 67 |
| Dark Horse Treating Plant | Pinon Midstream | Oil and gas wells within 2 miles of the Independence AGI wells | 54 |
| Red Hills Gas Processing Plant | Targa Northern Delaware | Oil and gas wells within 2 miles of the Red Hills AGI wells, plus the project wells | 45 |
| DKL Libby Gas Plant | DKL Delaware Operating - NM | No list in the posted plan (see below) | 0 |

The lists cover different footprints: a whole enhanced-recovery unit, a maximum monitoring area, a Class II area of review, or a fixed radius. Counts are not comparable from site to site.

Two new list roles appear in `plan_role`: `aor_well_list` (Titan) and `radius_well_list` (Red Hills, Dark Horse and the Metropolis table in the Maljamar plan). The others are as in v1.

## Results

| | |
|---|---|
| Sites | 7 |
| Sites whose plan lists wells by API number | 6 |
| Listed wells | 1,228 (no well is listed by two sites) |
| Matched to an OCD well record | 1,227 (99.9%) |
| OCD status of the listed wells | 696 active, 382 plugged, 113 new (permitted, not yet reported drilled), 19 cancelled, 16 temporarily abandoned, 1 with the code `Recl` |
| Listed wells that OCD carries only as a "PRE-ONGARD WELL" placeholder | 62 (61 plugged) |
| Plugged wells with a plug date in either OCD copy | 292 of 382 |

The one unmatched well is a Hobbs unit well (30-025-36011, NHSAU 923-29), which the plan lists as a shut-in gas producer.

## What New Mexico shows

**The digital record is more complete than in Texas, but it is not complete.** Every listed well but one has an OCD record with a location, so New Mexico has nothing like the 150 Texas wells with no digital record at all. But 62 listed wells appear in OCD's data only as placeholders. Their name is "PRE-ONGARD WELL #nnn" and their operator is "PRE-ONGARD WELL OPERATOR", meaning that the well predates OCD's ONGARD database and its details were never carried into it. None of the 62 has a spud date or a plug date in either copy of the OCD data I used. They are spread across five sites: 32 at Titan, 11 at Copperhead, 10 at Maljamar, 7 at Dark Horse and 2 at Red Hills. Sixty-one of them are plugged. This is the New Mexico version of the Texas paper-only wells. The state knows where the hole is and that it was plugged, but its digital record doesn't say when it was drilled or plugged, or by whom. Whatever exists is in OCD's scanned well files.

**Inventories age.** The Hobbs plan's well list is dated August 2016, and the posted plan is dated January 2017. Today OCD shows 239 of those 714 wells as plugged and 15 as temporarily abandoned. OCD shows 113 listed wells as new, meaning permitted but not yet reported drilled. 107 of them are at the four Delaware Basin sites, and 104 of the 113 are horizontals. Operators change too: of the 76 Titan rows that name Ameredev, 73 now show Matador as operator. An inventory frozen in a PDF stops being accurate as soon as it is filed, which is the third point in v1's list of what an observation network would need.

**One plan has no list.** The DKL Libby plan says its table of wells in the monitoring area is in Appendix C. The plan EPA has posted has no appendices; it ends with its references on page 88 of 88. The text names three wells that penetrate the injection zone, and those are in `site_wells_nm.csv` as references.

## Sources

1. **EPA Subpart RR plans.** These are the current approved plans for the seven sites, downloaded on 16 October 2026. URLs, sizes and SHA-256 hashes are in `sources_epa_mrv_plans_nm.csv`.
2. **OCD well data, as served by the New Mexico Environment Department's public map server** (`mercator.env.nm.gov`, service `emnrd/ocd_wells`, all five layers). I queried it by API on 16 October 2026. This copy is current; it includes Lea County APIs in the 30-025-54xxx range. It is the source for name, status, operator, location, direction, pools and the plug date (`nmocd_*` columns, `lat_nad83`, `lon_nad83`).
3. **The New Mexico State Land Office's copy of the same data** (`NMOCD_Wells_V3`). It is older: it has no Lea County API above 30-025-50999, so I didn't use it as the primary source. It does carry spud dates and true vertical depths, which the Environment Department copy leaves blank, so I used it for `nmslo_spud_date`, `nmslo_plug_date` and `nmslo_tvd_ft` only.

Details and the query notes are in `nmocd_source.json`.

## How it was built

- **Text lists.** I extracted each plan's text with PyMuPDF and found New Mexico API numbers (30, a county code, then five digits), allowing for spaces, missing hyphens and the 14-digit form. List pages and their roles are in `table_roles_nm.json`. All lists except Hobbs's start each row with the API, so the row text runs from one API to the next. Hobbs puts the well name before the API, and its rows are rebuilt cell by cell.
- **OCR.** Both well tables in the Maljamar plan are images with no text layer. I rendered those pages at 300 dpi and read them with Tesseract twice: once on the API column alone, restricted to digits and hyphens, and once on the whole row. For 189 of the 201 rows the two readings agree. For 11 others I read the API from the image by eye. One row, highlighted in a dark color on the page, wasn't picked up by the line detector, and I added it by eye. The rows are in `maljamar_ocr_rows.csv` and the code is in `scripts/ocr_maljamar.py`. As checks:
  - All 193 distinct OCR'd APIs match an OCD record.
  - For 174 of them, the OCD well name agrees with the name in the table. For 15 it agrees partly. The other 4 are names OCD doesn't have, because those wells are PRE-ONGARD placeholders.
  - For the 132 rows where the plan's coordinates were readable, the median distance to OCD's location is 0 m and the 90th percentile is 82 m. The 10 rows more than 500 m off each differ from OCD by one or two misread digits in the coordinate, not in the API.
- **Join.** I matched on the 10-digit API across all five OCD layers. No API returned more than one record.
- **Name check.** For every listed well, `name_check` records whether OCD's well name appears in the plan's row: `match`, `partial` or `no`. Hobbs uses its own unit numbering (for example "NHSAU 111-19"), so there the check only records whether OCD's name is a Hobbs unit name; 711 of 714 are.

## New columns in `site_wells_nm.csv`

The file keeps the v1 plan columns. The RRC columns are replaced with these:

| Column | Meaning |
|---|---|
| plan_roles_all | Every list role the API appears under (a project well can also be in the radius list) |
| plan_extraction | `text` or `ocr` |
| ocr_method | `two_ocr_passes_agree`, `resolved_by_visual_check` or `added_by_visual_check` |
| nmocd_match, nmocd_records | Join result and the number of OCD records |
| nmocd_well_name, nmocd_operator, nmocd_ogrid | As OCD records them |
| nmocd_pre_ongard | `yes` if OCD carries the well only as a PRE-ONGARD placeholder |
| nmocd_status | OCD status as served, cut to four letters: `Acti`, `Plug`, `New`, `Canc`, `Temp`, `Recl` |
| nmocd_well_type, nmocd_layer, nmocd_direction | Oil, gas, injection and so on; direction is V, D or H |
| nmocd_ulstr | Unit letter, section, township, range |
| nmocd_pools, nmocd_md_ft, nmocd_plug_date | Pools, measured depth and plug date (YYYYMMDD; blank where OCD has a placeholder date of 1900-01-01 or 9999-12-31) |
| nmocd_details_url | OCD's well details page |
| nmslo_spud_date, nmslo_plug_date, nmslo_tvd_ft | From the older State Land Office copy, with the same placeholder dates blanked |
| lat_nad83, lon_nad83 | OCD surface location |
| name_check | See above |
| ocr_location_check_m | For OCR'd rows, the distance between the plan's coordinates and OCD's |

`sites_nm.csv` has one row per site with the counts above. `site_wells_nm.geojson` has the 1,227 listed wells with a location, as points.

## Checking

Before publishing, a separate agent that hadn't built the dataset checked it with its own code. It confirmed:
- All seven PDF checksums.
- The API set of every text list, re-extracted with a different PDF library (pypdf). It matched site by site.
- Every OCR'd row, read by eye against the page images.
- OCD values for a random 60 wells plus the unmatched rows, queried independently. Name, status, operator and location all matched.
- That the State Land Office copy has no Lea County APIs in the 30-025-51xxx or 52xxx ranges.
- The DKL Libby and Hobbs points above.

It also found four problems, all fixed before publishing:
- One row of the Metropolis table had been dropped by the OCR.
- The 9999-12-31 placeholder had been read as a real date.
- One site count included the unmatched well.
- One status had been left out of a total.

## Limitations

- OCD data changes daily. These values are as of 16 October 2026.
- OCR can misread. Every OCR'd API matched an OCD well and almost all names and locations agree, and the independent check read every row again. Still, the source is a low-resolution image.
- List roles are my reading of the captions; the page ranges are published.
- No list for DKL Libby, for the reason above.

## License

Data: CC BY 4.0. Code: MIT.
