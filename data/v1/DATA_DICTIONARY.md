# Data dictionary

## sites.csv (one row per site)

| Column | Meaning |
|---|---|
| site_slug | Short ID, matching the EPA facility page path |
| site_name, operator_per_epa, uic_class | As listed on EPA's Subpart RR decisions table |
| epa_decision_date | Date of EPA's decision on the current plan |
| counties_from_rrc_matches | Counties of the matched wells, with counts |
| plan_well_list_type | Roles of the numbered well lists in the plan (see README) |
| plan_well_list_titles | Page ranges and table titles of those lists |
| apis_listed_in_well_lists | API numbers in those lists |
| apis_mentioned_elsewhere | API numbers mentioned only in text, figures or other tables |
| listed_matched_rrc_ewa / listed_unmatched | Join result for the listed APIs |
| listed_with_rrc_plug_date | Listed and matched wells with an RRC plug date (a lower bound on plugged wells) |
| plan_url, epa_page, plan_sha256, plan_retrieved_utc | Provenance of the plan PDF |

## site_wells.csv (one row per site and API number)

| Column | Meaning |
|---|---|
| site_slug, site_name | Site |
| api10 | Texas API number: 42 + county code (3) + well identifier (5). The identifier can contain a letter for some old records |
| plan_role | `unit_well_list`, `mma_well_list`, `legacy_penetrations_aor_mma`, `project_wells`, or `reference_in_text_figure_or_other_table` |
| plan_table_title | Caption of the list it came from |
| plan_entries | Times the API appears in the well list (more than 1 for multiple completions, sidetracks or repeat listings) |
| plan_type_raw, plan_status_raw | The operator's well type and status as printed, where parseable; distinct values joined with `;` |
| plan_row_raw | Each list entry's row text as extracted, joined with a double bar (or the first mention, for references) |
| plan_sidetrack_suffixes | Nonzero 11th-12th API digits printed in the plan (sidetracks merged into this row) |
| plan_pages | Plan PDF pages (1-based) where the API appears |
| plan_mentions | Number of mentions in the plan |
| plan_url | Source plan |
| rrc_match | `matched`, `no_match_in_EWA`, `no_match_nonnumeric_api`, or `placeholder_api` (well ID 00000) |
| note | Flag for a known source-plan error |
| rrc_rows | RRC rows for this wellbore |
| rrc_county, rrc_district, rrc_field_name, rrc_lease_name, rrc_operator_name, rrc_well_type | Most recent non-blank value (rows ordered by completion date, then W-2/G-1 filing date, then RRC row ID) |
| rrc_other_operators | Other operator names on this wellbore's RRC rows |
| rrc_oil_gas_code | All oil/gas codes on the wellbore's rows |
| rrc_depth_ft | Deepest recorded depth (blank if none) |
| rrc_plug_date, rrc_w3_file_date | Latest plug date and W-3 (plugging report) file date, YYYYMMDD |
| rrc_latest_completion_date | Latest completion date, YYYYMMDD |

Plugged wellbores in the RRC file often carry no operator, depth, type or completion date on any row. A blank means the RRC row is blank, not that the join failed.

## monitoring_keyword_screen.csv (one row per site)

Each method column counts the plan pages that mention any of that method's keywords. The patterns are in `scripts/monitoring_screen.py`. A count shows that a plan mentions a method, not that the operator has committed to it.

## sources_epa_mrv_plans.csv

URL, local file name, bytes, SHA-256 and retrieval time for each plan PDF, plus `in_scope` (yes or no). The RRC file's provenance is in `rrc_source.json`.

## scope.json, table_roles.json

The site list and the page ranges each well list was assigned from, as used by the scripts.