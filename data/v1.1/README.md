# Dataset v1.1: locations, and a correction to v1

*16 October 2026 - Gale*

v1.1 adds the Railroad Commission's well-location map layer to the v1 dataset. Every listed well found on the RRC map now has a surface location, a map symbol and a location-reliability code. The methods, sources and scope are the same as v1 (see `../v1/README.md`); this note covers only what changed.

## Correction to v1

v1 said the 392 listed wells with no match in the RRC wellbore file were "mostly dry holes, wells plugged long ago, wells with a spud date only, and permitted wells not yet drilled." With the map layer, that is wrong in the aggregate. The 392 split into three groups:

| Group | Wells | What they are |
|---|---|---|
| Recent wells not yet in the completion-based file | 223 | 200 are horizontal well surface locations, 19 are permitted locations and 4 are directional or sidetrack surface locations. Most are in Loving County (Milestone) and Yoakum County (Campo Viejo, 30-30). The wellbore file is built from completion filings, so wells that have not completed yet are not in it. |
| On the RRC map, but not in the wellbore file for other reasons | 19 | These include 5 dry holes, among them the three legacy dry holes at Brown Pelican, plus injection, shut-in and observation wells. |
| No record in either RRC digital dataset | 150 | 35 Denver Unit wells the operator lists as P&A. 40 South Plains wells, 36 of them listed inactive. 60 Milestone wells, mostly with old-style numbers and 27 with a letter in the identifier. 9 Campo Viejo wells, including 3 the operator lists as dry holes. 2 county placeholders. 4 others. |

The point v1 was making survives, at a smaller scale. About 150 wells that operators list in their storage-site monitoring areas leave no trace in the Railroad Commission's public digital data. By the operators' own descriptions, most are plugged, inactive or old. Some may be numbering errors in the plans; the public data can't tell those cases apart. The three Brown Pelican dry holes show a second kind of gap: they are on the RRC map as dry-hole symbols, but per the operator's own records search their construction and plugging records exist only in hardcopy or on microfilm.

## What's new in the files

- **`site_wells.csv`** keeps all the v1 columns and adds:
  - `rrc_map_found`: `yes`, `yes_bottom_only` or `no`
  - `rrc_map_symbol` and `rrc_map_symbol_code`: the RRC well symbol, such as Dry Hole, Plugged Oil Well or Horizontal Well Surface Location
  - `surface_lat_nad83`, `surface_lon_nad83`
  - `location_reliability` and `location_reliability_code`: how the RRC spotted the well, for example from a hardcopy map, aerial imagery or operator coordinates
  - `rrc_map_surface_points`, `rrc_map_bottom_points`
  - `any_rrc_record`
- **`sites.csv`** adds counts by group: `listed_on_rrc_map`, `listed_with_location`, `listed_not_in_ewa_but_on_map`, `listed_not_in_ewa_recent_or_permitted` and `listed_no_rrc_digital_record`.
- **`site_wells.geojson`** has the 11,271 listed wells that have a surface location, as points (NAD83). The properties are the main plan and RRC fields.

## Results

| | |
|---|---|
| Listed wells | 11,429 |
| With any RRC digital record (wellbore file or map) | 11,279 (98.7%) |
| With a surface location | 11,271 |
| With no RRC digital record | 150 |

Location sources for the listed wells:

| Source | Wells |
|---|---|
| RRC hardcopy map | 4,920 |
| USGS quad or aerial imagery | 2,327 |
| Operator coordinates | 2,092 |
| Operator distances and plat | 1,650 |
| Other | 282 |

## Source and check

The new source is the RRC's Well Layers by County, a public download containing a shapefile for each county. I fetched it on 16 October 2026 for the 16 counties that appear in the dataset; the per-file SHA-256 hashes are in `rrc_well_layers_provenance.jsonl`. Wells are joined on the 8-digit API. Where a wellbore has several surface points, I use the one with the highest RRC reliability code. Symbol and reliability meanings come from the RRC's Digital Map Information User Guide.

As a check, I compared the locations against the Milestone plan, which gives its own coordinates. For the 658 Milestone wells with coordinates in both sources, the median distance between the plan's position and the RRC map position is 0 m and the 90th percentile is 2 m. Four differ by more than 1 km; those are probably text-extraction mismatches in the plan's table.

## License

Data: CC BY 4.0. Code: MIT.