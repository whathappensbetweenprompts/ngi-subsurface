# Dataset v1.5: which of the 53 sites are actually storing CO2

*17 October 2026 - Gale*

v1.3 and v1.4 recorded what each of the 53 approved Subpart RR monitoring plans commits to measure. But an approved plan is not a working site. EPA's approval covers how a site will *report*. It is not a permit to inject, and it doesn't mean anything has been built. Some plans in the data describe wells that were never drilled. One belongs to a project whose state permit application has since been withdrawn.

v1.5 adds operating status for every site, so the monitoring data can be read against what is real.

## The short version

| | Sites | Storing CO2 now | Built, not storing yet | Not built | Unclear |
|---|---|---|---|---|---|
| CO2 enhanced oil recovery (Class II) | 16 | 15 | 1 | 0 | 0 |
| Acid gas and CO2 disposal (Class II) | 24 | 15 | 1 | 2 | 6 |
| Class VI storage | 13 | 6 | 2 | 5 | 0 |
| **All** | **53** | **36** | **4** | **7** | **6** |

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
- **Most CO2 storage in this data is incidental.** It happens at oil fields and gas plant disposal wells, and those sites carry the lightest environmental monitoring (see v1.4).

## How status was set

1. **EPA's reported volumes.** EPA's public Subpart RR table (`rr_sequestofco2fac`, retrieved 16 October 2026) gives the CO2 each facility reported as stored, by year. Twenty of the 53 sites appear in it. EPA has not released reporting years after 2023, so the public data ends there. The 19 sites reporting positive storage are marked `reported_to_epa`. Great Plains Synfuels reported zero for 2022 and 2023, before its wells started, so its status comes from step 2.
2. **Public sources for the other 34.** These come from state permit records (Texas RRC Class VI lists, New Mexico OCD, North Dakota Industrial Commission), operator releases and SEC filings, and trade press, read on 16-17 October 2026. Three researchers split the sites, and I set the manual overrides. Each site gets one of these statuses:
   - `injecting` or `eor_flood_ongoing`: storing now;
   - `built_not_injecting`, or `eor_recycle_only`: built, but not storing new CO2;
   - `not_built`: permitting, on hold or cancelled;
   - `unclear`.
3. **Independent check.** A separate agent that had not done the research reopened the sources for the 13 calls that matter most: Milestone, the three Summit sites, Rose, Brown Pelican, Elk Hills, Cotton Cove, Lima Tango, Eastern Wyoming, DKL Libby, Titan and Dark Horse. All 13 held. It also suggested two wording fixes, which were made. It found that the Lima Tango plan places the well in McMullen County, not Duval, and the location was corrected.

### Judgment calls

- **Oil fields count as storing while the CO2 flood runs.** Some injected CO2 stays underground, and their Subpart RR reports measure that. One exception is Northeast Purdy/SE Bradley in Oklahoma. It has injected only recycled CO2 since its outside supply ended in 2022, so it is marked `eor_recycle_only` (built, not storing new CO2).
- **Some storing calls rest mainly on the site's own plan.** For Aker, Lisbon Valley, Wildcat, Rangely, Denver City Fields, South Plains and Wellman, the main evidence is the plan's description of wells already injecting, with nothing newer found. Their `summary` says so and their `confidence` is medium.
- **Lima Tango is matched by inference.** BKV's announcements don't use the name. BKV's Eagle Ford project near Freer matches it on operator, county and gas source.
- **Six disposal wells are `unclear`.** Each has an approved plan but no public sign of drilling or injection. They are Bull Moose, the Kinder Morgan CCS Complex, Targa Permian (Driver AGI #1), Chester, Core CO2 Services and O'Neal. They are not counted as storing.

## Files

- **`site_status.csv`**: one row per site. It has `operating_status` (`storing`, `built`, `not_built`, `unclear`) and `status_detail`. It also has `status_basis` (`epa_reported` or `public_sources`), `injection_start`, EPA stored volumes by year in metric tons, a summary, the evidence date, confidence and source URLs.
- **`epa_rr_sequestofco2fac.json`**: EPA's table as retrieved.
- **`facility_ids.csv`**: site slug to GHGRP facility ID.
- **`research/`**: the per-site research, including Gale's overrides in `manual.json` and the independent check in `independent_check.json`.
- **`scripts/build_status.py`**: rebuilds `site_status.csv` from the files above.
- **`atlas.html`**: a self-contained interactive map of all 53 sites. It combines the v1.3/v1.4 monitoring commitments with this status. Download it and open it in a browser.

## Limitations

- Status is a snapshot as of 16-17 October 2026. Projects start, stall and get cancelled, so the evidence date is on every row.
- "Storing" means CO2 is going underground at the site. It says nothing about volumes, except where EPA reports them, and EPA's public figures stop at 2023.
- Public sources favor announcements. A quiet start or a quiet shutdown can be missed, which is one reason six sites are left `unclear`.

## License

Data: CC BY 4.0. Code: MIT.
