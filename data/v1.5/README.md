# Dataset v1.5: which of the 53 sites are actually storing CO2

*17 October 2026 - Gale*

v1.3 and v1.4 recorded what each of the 53 approved Subpart RR monitoring plans commits to measure. But an approved plan is not a working site. EPA's approval covers how a site will *report*. It is not a permit to inject, and it doesn't mean anything has been built. Some plans in the data describe wells that were never drilled. One belongs to a project whose state permit application has since been withdrawn.

v1.5 adds operating status for every site, so the monitoring data can be read against what is real.

## The short version

| | Sites | Storing CO2 now | Built, not confirmed storing | Not built |
|---|---|---|---|---|
| CO2 enhanced oil recovery (Class II) | 16 | 15 | 1 | 0 |
| Acid gas and CO2 disposal (Class II) | 24 | 16 | 5 | 3 |
| Class VI storage | 13 | 6 | 2 | 5 |
| **All** | **53** | **37** | **8** | **8** |

*Updated 17 October 2026: the six sites first left `unclear` are now settled from state well and injection records. See "State records" below.*

- **Dedicated storage is thin.** Six of the 13 Class VI sites are storing CO2. Five of those store their own CO2:
  - ADM's ethanol plant in Illinois;
  - the Red Trail and Blue Flint ethanol plants in North Dakota;
  - Great Plains Synfuels in North Dakota, injecting since February 2024;
  - California Resources' Elk Hills gas plant, which began injecting in May 2026.
- **One site stores CO2 for others.** Tallgrass's Eastern Wyoming Sequestration Hub takes ethanol CO2 piped in from Nebraska, starting in late 2025.
- **Texas has three Class VI sites. None is injecting.**
  - Brown Pelican has its permit and wells. It is waiting on Occidental's direct air capture plant, which is now due at the end of 2026.
  - Rose's wells were drilled in 2024, and the Railroad Commission approved its permit in September 2026. No injection has been reported.
  - Milestone's Loving County hub application is listed as withdrawn on the Commission's September 2026 Class VI list.
- **Three North Dakota Class VI sites will not be built as planned.** In August 2026 Summit gave up its storage permits #1 and #2. Permit #3 is in court.
- **Approval is not operation, even for small wells.** Two Texas disposal wells with approved plans have injected nothing for CO2 storage. Kinder Morgan's Katz well has reported no injection since November 2022, although its plan expected CO2 from June 2024. Targa's Driver AGI #1 has not been drilled.
- **Most CO2 storage in this data is incidental.** It happens at oil fields and gas plant disposal wells, and those sites carry the lightest environmental monitoring (see v1.4).

## How status was set

1. **EPA's reported volumes.** EPA's public Subpart RR table (`rr_sequestofco2fac`, retrieved 16 October 2026) gives the CO2 each facility reported as stored, by year. Twenty of the 53 sites appear in it. EPA has not released reporting years after 2023, so the public data ends there. The 19 sites reporting positive storage are marked `reported_to_epa`. Great Plains Synfuels reported zero for 2022 and 2023, before its wells started, so its status comes from step 2.
2. **Public sources for the other 34.** These come from state permit records (Texas RRC Class VI lists, New Mexico OCD, North Dakota Industrial Commission), operator releases and SEC filings, and trade press, read on 16-17 October 2026. Three researchers split the sites, and I set the manual overrides. Each site gets one of these statuses:
   - `injecting` or `eor_flood_ongoing`: storing now;
   - `built_not_injecting`, or `eor_recycle_only`: built, but not storing new CO2;
   - `built_injection_unconfirmed`: the well exists, but no injection evidence was found (used in step 3);
   - `not_built`: permitting, on hold or cancelled;
   - `unclear`.
3. **State records.** For Texas and Michigan wells, I checked public state records directly:
   - the Railroad Commission's monthly injection reports (Form H-10, on data.texas.gov);
   - its UIC well register;
   - its county well map;
   - Michigan EGLE's well database.
   These records take precedence over press and plans. They settled the six sites left `unclear` by step 2, and they rechecked three `injecting` calls that had rested on older evidence. Wildcat and Aker are confirmed. Mongoose reported zero for January 2026, its latest month, so it is kept as `injecting` with medium confidence. Details are in the next section.
4. **Independent check.** A separate agent that had not done the research reopened the sources for the 13 calls that matter most: Milestone, the three Summit sites, Rose, Brown Pelican, Elk Hills, Cotton Cove, Lima Tango, Eastern Wyoming, DKL Libby, Titan and Dark Horse. All 13 held. It also suggested two wording fixes, which were made. It found that the Lima Tango plan places the well in McMullen County, not Duval, and the location was corrected.

### State records

| Site | What the records show | Status |
|---|---|---|
| Bull Moose (TX) | BM AGI #1 began injecting acid gas in April 2025: about 1.6 million Mcf through July 2025, the latest month filed | storing |
| Kinder Morgan CCS Complex (TX) | Katz 2361 exists. It took produced water from 2013 to November 2022 and has injected nothing since, through September 2025 | built, not confirmed storing |
| Targa Permian / Driver AGI #1 (TX) | The UIC permit exists, but there is no API number, the record is not activated, and zero injection is reported through January 2026. No well appears at the location on the RRC map | not built |
| O'Neal No. 4 (TX) | An existing gas well. Its injection permit letter is dated August 2024, with an H-1 filing dated 31 August 2026. It is not activated, and no injection has been reported | built, not confirmed storing |
| Chester (MI) | Smith 3-21 is drilled and listed as a completed CO2 injection well, not yet active | built, not confirmed storing |
| Core CO2 Services (MI) | Pontisso 2-10 in the Charlton 10 reef is listed as an active CO2 injection well, and its original oil wellbore was plugged in November 2025. No injection volumes were found. The Chester 12 reef wells are still shut-in gas wells | built, not confirmed storing |
| Wildcat (TX) | Injection since 2019. Volumes fell about 95% in August 2025 and have continued at the lower rate through July 2026 | storing |
| Aker (TX) | Injection since 2012, through November 2025 | storing |
| Mongoose (TX) | Injection from August 2023, about 74,000 Mcf a month in late 2025. January 2026 reports zero | storing (medium confidence) |

H-10 volumes are acid gas or total gas in thousand cubic feet (Mcf), not tons of CO2. The query results are saved in `research/state_records_raw/`. A separate agent recomputed every number in this table from those files. It corrected five details, all fixed above, and its notes are in `research/state_records_check.json`.

### Judgment calls

- **Oil fields count as storing while the CO2 flood runs.** Some injected CO2 stays underground, and their Subpart RR reports measure that. One exception is Northeast Purdy/SE Bradley in Oklahoma. It has injected only recycled CO2 since its outside supply ended in 2022, so it is marked `eor_recycle_only` (built, not storing new CO2).
- **Some storing calls still rest mainly on the site's own plan.** For Lisbon Valley, Rangely, Denver City Fields, South Plains and Wellman, the main evidence is the plan's description of wells already injecting, with nothing newer found. Their `summary` says so and their `confidence` is medium. (Aker and Wildcat were in this group until the state records confirmed them.)
- **Lima Tango is matched by inference.** BKV's announcements don't use the name. BKV's Eagle Ford project near Freer matches it on operator, county and gas source.
- **"Built, not confirmed storing" covers different cases.**
  - Brown Pelican and Rose are waiting to start.
  - DKL Libby's well is drilled, but its system isn't complete.
  - Kinder Morgan's well has sat idle.
  - O'Neal's permit is not yet activated.
  - The Chester and Core CO2 wells are listed as CO2 injection wells, but no injection volumes were found.
  - Northeast Purdy/SE Bradley injects only recycled CO2.

  `status_detail` keeps these apart.

## Files

- **`site_status.csv`**: one row per site. It has `operating_status` (`storing`, `built`, `not_built`, `unclear`) and `status_detail`. It also has `status_basis` (`epa_reported`, `state_records` or `public_sources`), `injection_start`, EPA stored volumes by year in metric tons, a summary, the evidence date, confidence and source URLs.
- **`epa_rr_sequestofco2fac.json`**: EPA's table as retrieved.
- **`facility_ids.csv`**: site slug to GHGRP facility ID.
- **`research/`**: the per-site research. `state_records.json` holds the state-record findings, and `state_records_raw/` holds the query results behind them. Gale's overrides are in `manual.json`, and the independent check is in `independent_check.json`.
- **`scripts/build_status.py`**: rebuilds `site_status.csv` from the files above.
- **`atlas.html`**: a self-contained interactive map of all 53 sites. It combines the v1.3/v1.4 monitoring commitments with this status. Download it and open it in a browser.

## Correction to v1 and v1.1

v1 described the Railroad Commission's Wellbore Query Data (`OG_WELLBORE_EWA_Report.csv`) as the monthly statewide file, with RRC fields reflecting the 16 October 2026 download. The download date is right, but the file's contents are not that recent. Every row carries a December 2020 load date, and the newest completion, filing and shut-in dates in it are from late 2020. So v1's RRC fields (well type, status, operator) describe each well as of about the end of 2020.

v1.1 has a group of 223 "recent wells not yet in the completion-based file". These are wells completed or permitted after 2020, not just wells that have not completed. v1.1's map-layer locations and symbols come from a current download and are unaffected. A current replacement for the wellbore fields is a job for a later version.

## Limitations

- Status is a snapshot as of 16-17 October 2026. Projects start, stall and get cancelled, so the evidence date is on every row.
- "Storing" means CO2 is going underground at the site. It says nothing about volumes, except where EPA reports them, and EPA's public figures stop at 2023.
- Public sources favor announcements, so a quiet start or a quiet shutdown can be missed.
- State injection reports lag. The latest month filed differs by well, from September 2025 to July 2026.
- Outside Texas and Michigan, statuses still rest on press and plans.

## License

Data: CC BY 4.0. Code: MIT.
