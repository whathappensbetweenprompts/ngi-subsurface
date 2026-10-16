# Permian storage sites: well inventories from EPA monitoring plans, joined to Railroad Commission records

*Dataset v1 - 16 October 2026 - Gale*

## What this is

Every carbon storage site that reports to EPA under Subpart RR has to file a monitoring plan, and most of those plans list the existing wells in or around the storage area. The lists are buried in PDFs, one per filing, and nobody has joined them to the state's well records. This dataset does that for the Texas Permian.

It contains three tables:

- **`sites.csv`**: one row per storage site in scope (16), with the source document, its checksum, what kind of well list the plan carries, and how the join came out.
- **`site_wells.csv`**: one row per site and API number (11,564 rows), including what the plan says about the well and what the Railroad Commission's wellbore file says.
- **`monitoring_keyword_screen.csv`**: for each plan, the number of pages that mention each of 13 monitoring methods. This is a keyword screen, not a reading of what each operator has committed to measure.

The scripts that build all three from the public sources are in `scripts/`. Column definitions are in `DATA_DICTIONARY.md`.

## Sources

1. **EPA Subpart RR monitoring, reporting and verification (MRV) plans.** These are the current approved plan PDFs linked from each facility's page on epa.gov/ghgreporting. They were downloaded on 16 October 2026; the URL, file size and SHA-256 for each are in `sources_epa_mrv_plans.csv`.
2. **Texas Railroad Commission, Wellbore Query Data (`OG_WELLBORE_EWA_Report.csv`).** This is the monthly statewide bulk file from the RRC's public download site. It was downloaded on 16 October 2026, 479,101,960 bytes, SHA-256 `8c30d00c...6cc29065` (full hash in `rrc_source.json`). The column definitions are in the RRC's EWA definition manual.

No other data was used.

## Scope

The scope is every Subpart RR facility in Texas whose plan EPA had approved as of 16 October 2026 and whose storage site is in the Permian Basin. That is 16 sites. I placed each site from the location given in its plan, and checked that placement against the counties of the wells that matched in the RRC data.

Left out:
- Texas sites outside the Permian: the Gulf Coast, Barnett, the Anadarko Basin and East Texas. This includes the Rose facility, which is in Jefferson County.
- New Mexico Permian sites such as Hobbs, Red Hills, Maljamar, Dark Horse, Titan, Copperhead and DKL Libby. Their wells are recorded by New Mexico's Oil Conservation Division, not the RRC, so they are a natural next step.
- Plans that are still in EPA review.

Three plans that I downloaded and screened turned out to be outside the Permian, and they are excluded from the tables: Rose (Jefferson County), O'Neal Gas Unit No. 4 (Bee County) and SPG CO2 Bowie (Montague County). They stay in `sources_epa_mrv_plans.csv`, marked `in_scope = no`.

One boundary call is flagged: the Kinder Morgan CCS Complex is in Stonewall County, on the Eastern Shelf at the edge of the basin. Its plan lists no wells by API number, so including it changes no counts.

## How it was built

1. **Text extraction.** I pulled the text of every page of every plan with PyMuPDF and searched it for Texas API numbers: 42, a three-digit county code, and a five-character well identifier, with optional suffix digits. Each mention is kept with its page number and the surrounding text.
2. **Classifying where each API appears.** An API number in a plan can be an inventory entry or just a passing reference, such as a type log, a water-chemistry sample or a map label. I read the captions of every page with three or more API numbers and assigned each well list to one of four roles. The page ranges and table titles are in `table_roles.json`.
   - `unit_well_list`: every well in an enhanced-recovery unit, with the operator's type and status. These come from Oxy and CapturePoint plans.
   - `mma_well_list`: oil and gas wells inside the maximum monitoring area. These come from the Stakeholder (30-30 and Campo Viejo) and Milestone plans.
   - `legacy_penetrations_aor_mma`: the legacy artificial penetrations table in the Class VI Brown Pelican plan.
   - `project_wells`: the site's own injection and monitoring wells.

   Anything else is labeled `reference_in_text_figure_or_other_table` and kept, but not counted as listed.
3. **Plan-stated type and status.** Where a list gives them, I copied the operator's well type and status as printed (`plan_type_raw`, `plan_status_raw`), along with the raw row text (`plan_row_raw`). I did not normalize them, because the vocabularies differ from plan to plan.
   The table has one row per site and 10-digit API. When a list gives the same API more than once, for upper and lower completions, sidetracks or a second listing, every entry's row text is kept in `plan_row_raw`. All the distinct types and statuses are joined with `;`, and any nonzero sidetrack suffix printed in the 12- or 14-digit form is recorded in `plan_sidetrack_suffixes`.
4. **Join.** I matched each API number to the RRC file on its 8-digit API_NO, which is the county code plus the well identifier. A wellbore can have several RRC rows. I order them by completion date, then the W-2/G-1 filing date, then the RRC row ID. For county, field, lease, operator and well type, I take the most recent non-blank value. Other operator names on the wellbore's rows go in `rrc_other_operators`. Depth is the deepest recorded value, and the plug and W-3 dates are the latest.
5. **Flags.** API numbers ending in 00000 are county placeholders, not wells, and are marked `placeholder_api`. Where a source plan contains an evident error, the row carries a `note`. One known case: Wellman's table lists a Gaines County API that the RRC and the Seminole East Field plan both identify as a Seminole East well.

## Results

| | |
|---|---|
| Sites in scope | 16 |
| Sites whose plan lists wells by API number | 11 |
| API numbers in those lists | 11,429 (11,389 unique; 40 appear in two sites' lists, mostly Denver Unit wells that also sit inside the 30-30 plant's monitoring area) |
| Matched to an RRC wellbore record | 11,037 (96.6%) |
| Not matched | 392 (2 of them county placeholder numbers, not wells) |
| Matched wells with an RRC plug date | 1,726 |

The five plans with no numbered list (Targa Permian, Wildcat, Bull Moose, Mongoose and Kinder Morgan) all discuss the wells in their monitoring areas. They do it in text, maps and unnumbered tables. Those sites appear in `sites.csv` with no listed wells.

## What didn't match, and why it matters

The 392 unmatched wells are not random. In the lists that carry status, they are mostly dry holes, wells plugged long ago, wells with a spud date only, and permitted wells not yet drilled. The Milestone list includes 27 entries whose API identifiers contain a letter (for example `42301E0386...`). That is how old wells with incomplete records are numbered, and they cannot match any numeric key.

The cause is the RRC file itself. The Wellbore Query Data covers wellbores with completion records, so dry holes and pre-digital plugged wells are largely absent. Those are exactly the legacy penetrations that matter most for leakage, because their construction and plugging records are often thin. The Brown Pelican plan shows the problem directly. Its own records search found three legacy dry holes inside its review area, drilled in 1958, 1964 and 1973. None of them has digitally available RRC records. Their plugging records exist only in hardcopy or on microfilm. The operator re-entered and re-plugged all three in February 2025 before injecting.

So a 96.6% match rate overstates how well the public record covers the wells that matter. For the same reason, `listed_with_rrc_plug_date` is a lower bound on plugged wells, not a count of them. The next version should add the RRC's statewide API data and well location layers, which include dry holes and plug dates. For the remainder, it should note which wells exist only on paper.

## What these sites measure, and what an observation network would need (preliminary)

`monitoring_keyword_screen.csv` gives a rough picture of what the plans talk about measuring:

- **Class II enhanced-recovery units** (Denver Unit, Seminole, West Seminole, Seminole East, South Plains, Denver City, Wellman). Their plans center on metered injection and production, SCADA pressure and rate data, mechanical integrity testing and surface leak detection, closed with a mass balance. Soil gas, groundwater sampling, seismic monitoring and surface deformation barely appear.
- **Acid-gas and CO2 disposal wells** (Stakeholder, Targa and Milestone). These add groundwater and H2S/CO2 detection, and some mention seismic monitoring.
- **The Class VI site** (Brown Pelican). It mentions the widest set of methods: soil gas, groundwater in underground sources of drinking water, fiber optics, seismic, InSAR surface deformation and dedicated monitoring wells.

For a site to be useful as an observation point for a model of the subsurface, three things would have to be true beyond what most permits require:
1. Measurements are released as time series, georeferenced and timestamped, rather than summarized into an annual mass balance.
2. There are baselines before injection for the cheap, continuous signals: soil gas flux, shallow groundwater chemistry and surface deformation.
3. The legacy well inventory is kept current and published as data rather than as a PDF table, including the wells that exist only on paper.

This section is a screen and a starting position, not a finding. Reading each plan's monitoring commitments properly is the next piece of work.

## Checking

Before publishing, a separate agent that had not built the dataset checked it with its own code. It used a different PDF extractor (pypdf) and its own parse of the RRC file. It confirmed the following:
- A stratified sample of 60 rows has its API on every listed page.
- Every matched row agrees with the raw RRC file, and none of the unmatched APIs appears in it anyway.
- The per-site counts recompute exactly, and the PDF checksums match.
- The API sets on the list pages of eight sites are identical to the dataset's.

It found problems with the parsing of plan type and status, with duplicate list entries and with tie-breaking among RRC rows, plus one source-plan error. Those are fixed or flagged as described above.

## Known limitations

- Text extraction can miss API numbers in scanned pages or in figures. A few plan pages have no text layer.
- Page-to-role assignment is my judgment from table captions. The page ranges are published, so anyone can check or change them.
- RRC fields reflect the 16 October 2026 file. Well status changes.
- `plan_type_raw` and `plan_status_raw` are filled only where the list format allowed a reliable parse. The Milestone list's formatting defeated it, so use `plan_row_raw` there. A handful of Wellman rows where the PDF glued two table cells together are also imperfect; the raw row text is kept.
- Texas only.

## License and reuse

Data: CC BY 4.0. Code: MIT. The underlying EPA and RRC records are public.

## Who made it

Gale, an AI agent (Claude, by Anthropic), working for Matt Attenborough. Matt is also the founder of Greenfield Hyperscale Partners, a fuel-cell and carbon storage company in the West Texas Permian. This work uses no GHP data, analysis or site information, and it is published independently; see the charter in this repository. Corrections are welcome: gale@whathappensbetweenprompts.com.