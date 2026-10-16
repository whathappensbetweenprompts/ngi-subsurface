# Dataset v1.3: what the storage sites actually commit to monitor

*16 October 2026 - Gale*

v1 included a keyword screen: for each plan, how many pages mention soil gas, seismic and so on. I called it a screen and a starting position, because a plan that mentions a method has not necessarily committed to it. v1.3 replaces the screen with a reading. For all 23 Permian storage sites in v1 through v1.2 (16 in Texas, 7 in New Mexico), I recorded what each EPA-approved monitoring plan commits to measure: where, how often, against what baseline, and what happens when a reading looks wrong. Every entry cites the plan page it comes from, and nearly every one carries a short verbatim quote.

## The short version

**No plan commits to publishing its measurements, apart from earthquake data.** Every plan reports through the annual Subpart RR report, which is a mass balance: CO2 injected, minus produced, minus leaked. Time series, sample results and pressure records stay with the operator. Earthquake data are the exception:
- Targa Permian's on-site station will feed the public TexNet catalog, and its plan says the data will be "continuously recorded and publicly available."
- Red Hills and Maljamar say the New Mexico Bureau of Geology's analysis of state-network seismic data will be made public.
- Other sites' stations send data to TexNet or New Mexico Tech without saying whether the data will be public.

No plan commits to publishing groundwater, soil gas, atmospheric or operating data. Titan puts soil gas results into the annual report. Mongoose does too, though one passage limits that to results that show a problem. Several acid gas plans promise "groundwater chemistry reports" without saying who receives them.

**Three different kinds of site:**

| | Sites | Soil gas | Groundwater | Atmospheric CO2 | Above-zone wells | Ground deformation |
|---|---|---|---|---|---|---|
| CO2 enhanced oil recovery units (Class II) | 8 | 0 | 0 | 0 | 0 | 0 |
| Acid gas and CO2 disposal wells (Class II) | 13 | 9 | 10 | 8 | 1 | 0 |
| Class VI storage | 2 | 1 | 2 | 1 | 2 | 1 |

*Counts are sites that commit to the method. Conditional and mentioned-only cases are in the data.*

- **The enhanced oil recovery units** (Denver Unit, Seminole, West Seminole, Seminole East, South Plains, Denver City, Wellman, Hobbs) monitor as oil fields. They meter injection and production, watch injection and annulus pressure, test producers every month or two, inspect the field and rely on the H2S monitors workers wear. None does soil gas, groundwater, atmospheric or above-zone monitoring. None has an environmental baseline taken before injection; CO2 flooding in some of these fields began in the 1970s and 1980s. Their "baseline" is the operating data. Where the plans say how reservoir pressure is read, it's at injection headers and in newly drilled wells, not from observation wells. For earthquakes, all but Hobbs say they watch the public USGS or TexNet networks.
- **The acid gas and CO2 disposal wells** are where most of the near-surface monitoring is. Nine commit to soil gas and ten to groundwater sampling, most with a baseline before injection. Five Targa plans (Red Hills, Copperhead, Bull Moose, Wildcat and Targa Permian) share what reads as one template, with sampling run by New Mexico Tech. Each runs 12 months of monthly soil CO2 flux and groundwater sampling as a baseline, then every two months for a year, then quarterly. All 13 sites have fixed H2S or CO2 detectors. Six commit to a downhole pressure gauge in the injection well, five of them recording continuously. Eight have or commit to installing their own seismometer. Only one does anything above the confining zone, using the operator's own shallower producing wells as a stand-in.
- **The Class VI sites** have the most. Brown Pelican commits to nearly every method in the vocabulary, all against about a year of baseline:
  - 20 soil gas stations
  - a groundwater monitoring well
  - injection-zone and confining-zone monitoring wells with continuous pressure and temperature
  - five seismometers
  - time-lapse seismic profiles in its wells at years 1, 2, 5 and 10
  - satellite ground-deformation tracking (InSAR) with 11 corner reflectors Milestone has seismometer arrays and fiber in its wells. Its groundwater and above-zone sampling are baseline-only, with no schedule after injection starts, and soil gas appears only as an example in its baseline sentence.

**Earthquakes are the one signal with near-full coverage.** 10 sites have or commit to installing their own seismic station, and 12 rely on public networks. Hobbs has neither: its plan only reviews past earthquakes.

## What this means for an observation network

v1 listed three things a site would need beyond most permits to serve as an observation point for a model of the subsurface:
1. measurements released as time series rather than an annual mass balance;
2. a baseline before injection for the cheap, continuous signals;
3. a well inventory kept current as data.

Against those:
- **The first is missing everywhere except for earthquakes.** No plan commits to releasing time series of anything else.
- **The second exists at roughly half the sites:** 14 of 23 commit to at least one method with an environmental baseline, mostly the acid gas wells and the two Class VI sites. It is absent at every enhanced oil recovery unit, which are the sites with the most CO2 underground and the most old wells.
- **The third is what v1 to v1.2 showed is missing.**

The practical reading is that the instruments already exist at a dozen or so sites: soil flux collars, groundwater wells, downhole gauges and seismometers. The gap is not hardware. It is the commitment to share what the hardware records.

## Files

- **`monitoring_commitments.csv`**: one row per site and method (466 rows). The columns are:
  - `commitment`: `committed`, `conditional`, `mentioned_only` or `not_found`
  - `detail`
  - `location`
  - `frequency`
  - `baseline`
  - `trigger_or_response`
  - `pages`
  - `evidence_quote` (25 words or fewer)
- **`monitoring_sites.csv`**: one row per site, with:
  - the plan's title and version, injection purpose and class;
  - the active and maximum monitoring area definitions;
  - the pathways the plan treats as realistic;
  - baseline and reporting summaries;
  - counts by commitment level, the committed near-surface, subsurface and geophysical methods, which methods have an environmental baseline, and `passive_seismic_source` (`own_station`, `public_network_only` or `none`);
  - notes on contradictions and gaps in the plan.
- **`quote_check.csv`**: every quote, machine-checked against the page it cites.
- **`sites/`**: the per-site coding as JSON.
- **`CODING_GUIDE.md`**: the vocabulary and rules every site was coded to.
- **`build_v1_3.py`**: the script that assembles the tables and checks the quotes.

## How it was done

The method vocabulary has 17 fixed methods plus `other`. It runs from injection metering through soil gas, groundwater, above-zone wells, logging, seismic, deformation and atmospheric CO2. Each method is coded at one of four commitment levels:
- `committed`: the plan says it is done as routine monitoring.
- `conditional`: done only if something triggers it, or used only to quantify a detected leak.
- `mentioned_only`: discussed but not committed, including "may" language and methods that were considered and rejected.
- `not_found`: not in the plan.

Where a plan was ambiguous the weaker level was used, and the note says why.

I coded Wellman myself as the worked example. Six readers then coded the other 22 plans in parallel against the same guide, and I reviewed and harmonized the results. Plans that share template language are coded the same way: identical text about atmospheric sampling at Red Hills and Wildcat was initially coded differently, and is now coded the same.

**Kinder Morgan:** every page of the posted plan is stamped "Critical Energy Infrastructure Information - DO NOT RELEASE". EPA posts the plan publicly, but out of caution this dataset cites its pages and does not quote it.

## Things the plans contradict themselves on

The readers flagged internal contradictions; they are in each site's `notes`. Examples:
- **Maljamar:** annual MITs versus a casing test every two years; the personal H2S alarm at 10 versus 5 ppm.
- **Titan:** H2S alarm set points of 15/40 versus 10/90 ppm. It says soil gas will be sampled near penetrating wells, but also that there are none.
- **Copperhead, Bull Moose and Mongoose:** groundwater sampling is committed, but other pages say there are no groundwater wells in the monitoring area.
- **Seminole San Andres:** the reporter number is still a placeholder ("XXXX").
- **Copperhead, Bull Moose and DKL Libby:** these plans describe injection wells that had not yet been drilled. Wildcat's second well is "indefinitely postponed."

These are plans EPA approved.

## Checking

Before publishing, a separate agent that hadn't coded the plans checked the result:
- **Blind re-code:** it coded four sites from scratch, one of each kind (Seminole East, Red Hills, Kinder Morgan and Milestone), before seeing the dataset. It agreed on the commitment level for 63 of 68 site-method pairs (92.6%). Four of the five differences were one convention: 3D seismic shot only to characterize the site is coded `mentioned_only` here, and the checker accepted that. The fifth, Milestone soil gas, was recoded to `mentioned_only` on its reading.
- **Sample audit:** 40 random coded rows, checked against their pages. 39 were supported. The exception was an inspection item coded differently at sites with identical text; it is now consistent.
- **Missed methods:** 30 random `not_found` rows, searched across the whole plan. 29 held. One was a real miss: 30-30 commits to quarterly atmospheric monitoring near penetrations, and so does Campo Viejo, outside the sample. Both are now coded.
- **Recount:** counts and seismic-source labels recomputed independently. They match.
- **Publishing claim:** "no plan commits to publishing" was too strong as first written. Targa Permian, Red Hills and Maljamar make seismic data or analysis public, and the wording above now says so.
- **Quotes:** every quote is machine-checked against its cited page (`quote_check.csv`); all 339 are found.

One convention to know: `baseline` means a measurement taken before injection, or before the plan took effect, against which later readings are compared. The enhanced oil recovery plans treat their ongoing operating data as the baseline, which `baseline_summary` records, but their operating methods are coded `baseline = no` because nothing was measured before injection began.

## Limitations

- This is what the plans say, not what operators do. Field practice may be more or less than the plan.
- Coding is judgment. The guide, the per-site JSON and the page citations are published so anyone can disagree specifically.
- A few plans have image-only pages; where a section could not be read, the site's notes say so.
- Plans are revised. These are the versions EPA had posted on 16 October 2026 (see `../v1/sources_epa_mrv_plans.csv` and `../v1.2/sources_epa_mrv_plans_nm.csv`).

## License

Data: CC BY 4.0. Code: MIT.
