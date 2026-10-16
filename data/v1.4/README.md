# Dataset v1.4: monitoring commitments for every approved Subpart RR site in the country

*16 October 2026 - Gale*

v1.3 read what the 23 Permian storage sites commit to monitor. v1.4 does the same for every other site whose Subpart RR monitoring plan EPA has approved: 30 more plans across eight states, from North Dakota's Class VI hubs to Michigan's pinnacle reefs and California's Elk Hills. With v1.3, that makes all 53 approved plans EPA lists as of 16 October 2026.

One site on EPA's list has no plan posted (CV Carbon, listed under "Multiple" states, with a decision letter only), so it is not in the data. Twelve more plans are still under EPA review and aren't posted.

## The national picture

| | Sites | Soil gas | Groundwater | Atmospheric CO2 | Above-zone monitoring | Repeat seismic | Ground deformation | Pre-injection environmental baseline |
|---|---|---|---|---|---|---|---|---|
| CO2 enhanced oil recovery (Class II) | 16 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| Acid gas and CO2 disposal (Class II) | 24 | 13 | 17 | 9 | 5 | 0 | 0 | 20 |
| Class VI storage | 13 | 9 | 13 | 3 | 13 | 11 | 1 | 13 |

*Counts are sites that commit to the method. The last column counts sites committing to at least one environmental method (soil gas, groundwater, atmospheric, seismic or deformation) with a baseline taken before injection.*

The Permian pattern holds nationally, and more sharply:

- **Enhanced oil recovery units monitor as oil fields, everywhere.** Across 16 units in Texas, New Mexico, Oklahoma, Colorado and Michigan:
  - none commits to soil gas, atmospheric monitoring, repeat seismic or ground deformation;
  - only one samples groundwater (Northeast Purdy/Southeast Bradley in Oklahoma);
  - only one monitors above the confining zone (Petra Nova's West Ranch);
  - none has a pre-injection environmental baseline;
  - for earthquakes, nine have nothing beyond a one-time look at the historical record, and seven watch public networks.
- **Class VI storage is built for observation.** All 13 Class VI sites commit to groundwater sampling, above-zone monitoring and repeat well logging, and all 13 have a pre-injection environmental baseline. Eleven commit to repeat seismic imaging of the plume, and ten have their own seismometers. The North Dakota plans and ADM's Illinois site commit to the fullest sets of methods.
- **Class II disposal wells sit in between.** Twenty of the 24 sample soil gas or groundwater against a baseline, and 11 have their own seismometer. Only five look above the confining zone, and none images the plume.

**No plan anywhere commits to publishing its measurements.** Every one of the 53 reports through the annual Subpart RR mass balance. Several share data with the state regulator: Michigan's EGLE, North Dakota's UIC program, the Texas RRC, Colorado's COGCC and California's CalGEM. The two Summit plans share flowline data between affiliated operators. None publishes time series. As in the Permian, the exception is earthquake data, where some site stations feed public networks.

**So for an observation network:** 37 of the 53 sites commit to soil gas, groundwater, atmospheric or above-zone monitoring: all 13 Class VI sites, 22 of the 24 disposal wells and 2 oil recovery units. The collars, shallow wells, monitoring wells, gauges and seismometers are installed or committed, and most have baselines. What is missing everywhere is a commitment to release what those instruments record.

## How v1.4 was coded

The same coding guide as v1.3 (`../v1.3/CODING_GUIDE.md`), with the same 17-method vocabulary and the same conventions. There were three differences in how the work was done:

1. **API batch.** The 30 plans' text went to Claude Fable 5.1 through Anthropic's Message Batches API, with the coding guide and the Wellman worked example as the system prompt (`api_system_prompt.md`). That's one request per plan, about 1.96 million input tokens in total. 29 came back coded.
2. **One plan was hand-coded.** The API declined to process ADM's Illinois Class VI plan, on both Fable and Opus. The cause turned out to be the plan's text layer: the PDF's fonts lack Unicode mappings, so the extracted text is gibberish. A reader in session re-downloaded the PDF (its SHA-256 matches the recorded hash), OCR'd the monitoring sections and coded them by hand. The row is marked `coded_by = hand_coded_in_session`. The MRV plan itself is 37 pages and covers the CCS#2 well; most of the rest of the 594-page file is the Class VI permit and its testing and monitoring plan, which the plan incorporates.
3. **Quote check.** All 484 quotes in v1.4 were machine-checked against their cited pages. The 467 from the API-coded plans all match. ADM's quotes were checked against a separate OCR of the cited pages: 16 of 17 match exactly, and the 17th differs by one OCR misread ("CCSH1" for "CCS#1", p23).

## Checking

A separate agent checked the API-coded results before publishing:

- **Blind re-code:** it re-coded four sites from scratch, one of each type: Farnsworth, Shute Creek, Great Plains Synfuels and Lima Tango. It agreed on the commitment level for 66 of 68 site-method pairs (97.1%). Both differences were borderline cases about well logs that were not part of monitoring; both are now coded `mentioned_only`.
- **Sample audit:** 50 random coded rows. There was no over-coding (no "may" or "could" coded as committed). The guide's conventions held. There were four small issues: one frequency, one baseline flag, one conditional, and one inconsistent placement of fiber-optic temperature sensing across three plans with identical text. All four are fixed.
- **Missed methods:** 40 random `not_found` rows, searched across the whole plan. There were no misses.
- **Site-level fields:** purpose, class, version date and every data-sharing claim, checked for 10 sites. All were supported.
- **Page numbers:** one plan (Shute Creek) had cited printed page numbers instead of PDF pages. Its citations were corrected.

The checker's overall judgment was that the API-coded rows are about as reliable as a careful human reading on commitment levels, and that the most common defect was page citations.

**What it cost:** about $18 in API credits for the Fable batch (1.96M input and 0.31M output tokens at batch prices), plus about $2 for the declined Opus retry on ADM.

## Files

- **`national_monitoring_commitments.csv`**: all 53 sites, one row per site and method (1,079 rows), in the v1.3 columns.
- **`national_monitoring_sites.csv`**: one row per site. It adds `state`, `region` (`permian` or `outside_permian`), `site_group` (`eor`, `class_ii_disposal` or `class_vi_storage`) and `coded_by` to the v1.3 site columns.
- **`monitoring_commitments.csv`**, **`monitoring_sites.csv`** and **`quote_check.csv`**: the 30 v1.4 sites alone.
- **`sites/`**: per-site JSON for the 30 v1.4 sites. The Permian 23 are in `../v1.3/sites/`.
- **`sources_national.csv`**: the plan URL, file size, SHA-256, page count, image-only pages and token count for each plan.
- **`epa_rr_table.json`**: EPA's Subpart RR facility tables as retrieved.
- **`api_system_prompt.md`**: the exact system prompt sent with each plan.
- **`scripts/`**: the scripts for each step:
  - listing the EPA table;
  - fetching plans;
  - submitting the batch (it reads the API key from a local file and never prints it);
  - collecting results;
  - building and quote-checking;
  - OCR for ADM;
  - combining with v1.3.

## Limitations

- These are what the plans say, not what operators do in the field.
- `active_seismic` counts repeat seismic surveys of the plume. Seismic shot only to characterize the site is `mentioned_only`, by convention.
- Four sites carry `co2_disposal` in `injection_purpose`. They are grouped with acid gas disposal in `site_group`, because both are Class II disposal.
- The ADM QASP tables on rotated pages 130-145 were not read.
- Plans get revised. These are the versions EPA had posted on 16 October 2026.

## License

Data: CC BY 4.0. Code: MIT.
