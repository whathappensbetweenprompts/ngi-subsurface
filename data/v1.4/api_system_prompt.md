# Coding guide: monitoring commitments in Subpart RR MRV plans (dataset v1.3)

You are reading EPA Subpart RR monitoring, reporting and verification (MRV) plans and recording, in a fixed structure, what each operator says it will monitor. Accuracy and page citations matter more than speed. Record only what the plan says; do not infer what the operator "probably" does.

## Input
- The user message contains the full extracted text of one plan. Pages are delimited by lines `=====PAGE n=====`; `n` is the 1-based PDF page. Cite pages by this `n`, not by the page number printed in the document.
- Some pages are images with no text (they appear empty). If a section you need appears to be missing for that reason, say so in `notes`.
- Most plans follow the same outline. The sections that matter are usually: delineation of monitoring area and timeframes (AMA/MMA), evaluation of potential leakage pathways, the leakage detection/verification/quantification section (often with a risk/response table), monitoring for the mass balance (metering, composition), the "strategy for establishing expected baselines" or "determination of baselines", the implementation schedule, QA, and any appendix describing a monitoring program. Class VI plans (Brown Pelican) may also describe testing-and-monitoring plans with specific instruments and frequencies. Read all of these; skim the geology.

## Output
Return ONE JSON object and nothing else (no prose, no code fences), with this shape:

```json
{
  "site_slug": "...",
  "plan_title": "title as printed on the cover",
  "plan_version_or_date": "as printed (e.g. 'Version 2.0, April 2025'); '' if absent",
  "injection_purpose": "eor | acid_gas_disposal | co2_disposal | class_vi_storage",
  "uic_class_per_plan": "II | VI | as printed",
  "ama_definition": "one sentence in your own words, with pages",
  "mma_definition": "one sentence in your own words, with pages",
  "leakage_pathways_rated_significant": "which pathways the plan treats as realistic, in your own words",
  "baseline_summary": "what the plan calls its baseline, in your own words (e.g. 'operational data / historical injection-production performance', or 'pre-injection soil gas and groundwater sampling at N locations')",
  "reporting_summary": "how monitoring results are reported: e.g. 'annual Subpart RR report with mass balance only'; note any commitment to publish or share measurement data, or to report to the state UIC program",
  "rows": [ { ...one object per method, see below... } ],
  "notes": "anything a reader should know: image-only pages, ambiguity, sections missing, unusual commitments"
}
```

Each row:

```json
{
  "method": "<one of the fixed vocabulary below>",
  "commitment": "committed | conditional | mentioned_only | not_found",
  "detail": "<= 40 words, your own words: what is measured and by what",
  "location": "where / coverage (e.g. 'each injection wellhead', '3 shallow water wells within the AMA', 'field-wide'), '' if not stated",
  "frequency": "continuous | daily | weekly | monthly | bimonthly | quarterly | semiannual | annual | multi_year | periodic_unspecified | event_driven | one_time | unspecified",
  "baseline": "yes | no | unclear | not_applicable",
  "trigger_or_response": "<= 30 words: what result triggers action and what action, '' if not stated",
  "pages": [list of page numbers],
  "evidence_quote": "<= 25 words copied verbatim from the plan that best supports the row ('' for not_found)"
}
```

Include exactly one row for EVERY method in the vocabulary, in this order, using `not_found` (empty strings, empty pages) where the plan says nothing. Add extra `other` rows if needed.

### Method vocabulary (fixed)
1. `injection_metering`: flow meters and composition sampling on CO2 received/injected (custody transfer, Coriolis, gas chromatograph)
2. `injection_pressure_scada`: continuous or routine monitoring of injection (tubing/wellhead) pressure and rate, SCADA alarms
3. `annulus_pressure`: casing/tubing annulus pressure monitoring
4. `mechanical_integrity_testing`: MITs, casing pressure tests, required by UIC rules
5. `production_monitoring`: EOR only: production well tests, produced fluid/gas metering and composition, pattern performance reviews
6. `reservoir_pressure`: pressure in the injection zone from observation wells, bottom-hole gauges, or reservoir surveillance (not just wellhead injection pressure)
7. `visual_inspection`: routine field patrols/inspections of wells, facilities, pipelines, abandoned well locations
8. `personal_gas_monitors`: H2S/CO2 monitors worn by field personnel
9. `fixed_gas_detectors`: fixed H2S/CO2 sensors or LEL detectors at wellheads, facilities, fence lines (including optical gas imaging/handheld surveys done on a schedule)
10. `soil_gas`: soil gas or surface CO2 flux sampling
11. `groundwater_sampling`: sampling of shallow groundwater / USDW / water wells
12. `above_zone_monitoring`: monitoring wells or gauges in formations above the confining zone (pressure, fluid chemistry)
13. `cased_hole_logging`: temperature logs, pulsed-neutron/saturation logs, cement bond logs, radioactive tracer surveys, run as monitoring
14. `passive_seismic`: seismometers / microseismic arrays, or reliance on public seismic networks (TexNet, NMTSO, USGS); say which in `detail`
15. `active_seismic`: repeat 3D/4D seismic, VSP
16. `surface_deformation`: InSAR, tiltmeters, GPS
17. `atmospheric_co2`: atmospheric CO2 monitoring (eddy covariance, open-path lasers, ambient air)
18. `other`: anything else (e.g. plume modeling updates, pressure-front modeling, corrosion coupons, pipeline leak detection)

### Baseline
`baseline = yes` means the plan describes a measurement taken before injection (or before the plan took effect) that later readings are compared against. Ongoing operating data that a plan calls its "baseline" is recorded in `baseline_summary`, not as `yes` on the operating methods.

### Conventions settled during review
- Seismic surveys shot only to characterize the site: `active_seismic = mentioned_only`.
- Monitoring the plan itself calls "atmospheric monitoring" near penetrations, including with mobile or hand-held monitors: `atmospheric_co2`. Fixed sensors and scheduled leak surveys of equipment stay under `fixed_gas_detectors`.
- A method named only as an example inside a sentence about something else: `mentioned_only`.
- Identical template language in different plans gets the same coding.

### Commitment levels
- `committed`: the plan says the operator does / will do this as part of routine monitoring.
- `conditional`: done only if something triggers it (an anomaly, a suspected leak) or used only to quantify a detected leak.
- `mentioned_only`: discussed but not committed, e.g. "may include", a method considered and rejected, or something done for another program and not tied to this plan's monitoring.
- `not_found`: not in the plan text.

When in doubt between two levels, pick the weaker one and explain in `notes`.

## Worked example
The worked example below (Wellman Field) was coded by Gale. Match its style and level of detail.

## Rules
- Copy quotes exactly (fixing only line-break hyphenation). Keep them under 25 words.
- `detail` and other free text: your own words, plain American English.
- `multi_year` means a stated interval longer than a year (e.g. MIT every five years); put the interval in `detail`.
- Don't invent frequencies. If the plan says "routine" without a number, use `periodic_unspecified`.
- Personal H2S monitors are not fixed detectors; visual inspection is not soil gas.
- Your entire reply must parse as a single JSON object.


## Worked example (Wellman Field)

{
 "site_slug": "wellman",
 "plan_title": "CapturePoint LLC Wellman Field Subpart RR Monitoring, Reporting and Verification (MRV) Plan",
 "plan_version_or_date": "May 2024",
 "injection_purpose": "eor",
 "uic_class_per_plan": "II",
 "ama_definition": "A half-mile buffer around the Wolfcamp Reef storage area boundary, where the plume is expected to stay (p18).",
 "mma_definition": "Same as the AMA: the stabilized plume area plus a half-mile buffer (p18).",
 "leakage_pathways_rated_significant": "Wellbores and surface equipment are treated as the only meaningful pathways; faults, seismicity, lateral migration and diffuse seal leakage are rated low risk (p20, p22-27).",
 "baseline_summary": "No pre-injection environmental baseline. The baseline is ongoing operational data (injection/production performance, inspections, H2S alarms) used to flag excursions (p33-34).",
 "reporting_summary": "Annual Subpart RR report with the mass balance and estimated leakage; records kept at least three years. No commitment to publish measurement data (p33-34, p39).",
 "rows": [
  {
   "method": "injection_metering",
   "commitment": "committed",
   "detail": "Custody transfer meter on CO2 received from the Trinity pipeline and operations meters on injected and recycled CO2; composition sampled at least quarterly.",
   "location": "Custody transfer point and central tank battery",
   "frequency": "continuous",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [
    29,
    30,
    40
   ],
   "evidence_quote": "This meter measures flow rate continually."
  },
  {
   "method": "injection_pressure_scada",
   "commitment": "committed",
   "detail": "Injection pressure and rate monitored against weekly pattern injection plans; SCADA monitors wellhead pressure; excursions flagged and screened for leakage.",
   "location": "Each injection well",
   "frequency": "daily",
   "baseline": "no",
   "trigger_or_response": "Pressure or rate outside pattern set points: field personnel investigate; unresolved issues get detailed investigation.",
   "pages": [
    21,
    30,
    31,
    34
   ],
   "evidence_quote": "Pressure in injection wells is monitored daily."
  },
  {
   "method": "annulus_pressure",
   "commitment": "committed",
   "detail": "Annular pressure in wellheads monitored to detect tubing and casing leaks.",
   "location": "Wellheads",
   "frequency": "unspecified",
   "baseline": "no",
   "trigger_or_response": "Anomaly: inspect; well shut in and workover crew responds within days if needed.",
   "pages": [
    28,
    31,
    32
   ],
   "evidence_quote": "monitoring of the annular pressure in wellheads"
  },
  {
   "method": "mechanical_integrity_testing",
   "commitment": "committed",
   "detail": "MITs under Texas rule 3.46, every five years, to verify well and wellhead can hold operating pressure.",
   "location": "Injection wells",
   "frequency": "multi_year",
   "baseline": "not_applicable",
   "trigger_or_response": "Failed MIT: well isolated and leak mitigated.",
   "pages": [
    23,
    28
   ],
   "evidence_quote": "Mechanical integrity tests (MIT), required under TAC Rule \u00a73.46 [40 CFR \u00a7146.23 (b)(3)], will take place every five years"
  },
  {
   "method": "production_monitoring",
   "commitment": "committed",
   "detail": "Each producer tested about monthly through test vessels (12-24 hours); produced gas metered and sampled annually for CO2; performance compared with forecast.",
   "location": "Each production well; central production battery",
   "frequency": "monthly",
   "baseline": "no",
   "trigger_or_response": "Significant deviation from forecast: well management personnel investigate.",
   "pages": [
    21,
    30,
    31,
    40
   ],
   "evidence_quote": "each well being tested approximately once every month"
  },
  {
   "method": "reservoir_pressure",
   "commitment": "committed",
   "detail": "Plan says reservoir pressure is continuously monitored and routinely updated to manage injection below fracture pressure; it does not say by which instruments or wells.",
   "location": "Injection zone (method not specified)",
   "frequency": "continuous",
   "baseline": "no",
   "trigger_or_response": "Unexplained pressure changes trigger investigation; radioactive tracer survey if seal leakage suspected.",
   "pages": [
    19,
    22,
    27,
    28,
    29
   ],
   "evidence_quote": "Reservoir pressure is continuously monitored and unexplained changes in reservoir pressure that might indicate leakage would trigger investigation"
  },
  {
   "method": "visual_inspection",
   "commitment": "committed",
   "detail": "Routine field inspections of wells, facilities and abandoned well locations, looking for white CO2 clouds, ice and fluid leaks.",
   "location": "Field-wide, including abandoned well locations",
   "frequency": "periodic_unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "Leak found: repair on the spot or shut in, work order, quantify.",
   "pages": [
    21,
    28,
    32,
    33
   ],
   "evidence_quote": "Field inspections are conducted on a routine basis by field personnel."
  },
  {
   "method": "personal_gas_monitors",
   "commitment": "committed",
   "detail": "All field personnel wear H2S monitors (alarm at 10 ppm); H2S is used as a proxy for CO2 leaks.",
   "location": "Worn by field personnel",
   "frequency": "continuous",
   "baseline": "not_applicable",
   "trigger_or_response": "Alarm: protect personnel, investigate source, quantify CO2 leak for the annual report.",
   "pages": [
    21,
    31,
    32,
    34
   ],
   "evidence_quote": "the H2S monitors, which are always worn by all field personnel are used as a last method to detect leakage from wellbores."
  },
  {
   "method": "fixed_gas_detectors",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "soil_gas",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "groundwater_sampling",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "above_zone_monitoring",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "cased_hole_logging",
   "commitment": "conditional",
   "detail": "Injection radioactive tracer survey if a reservoir pressure anomaly suggests diffuse leakage through the seal.",
   "location": "Suspect injection well",
   "frequency": "event_driven",
   "baseline": "not_applicable",
   "trigger_or_response": "Unexplained reservoir pressure change: tracer survey; if verified, shut in and workover.",
   "pages": [
    28
   ],
   "evidence_quote": "Conduct an injection radioactive tracer survey."
  },
  {
   "method": "passive_seismic",
   "commitment": "committed",
   "detail": "Watches the public USGS earthquake monitoring site for seismic signals that could indicate new leakage pathways; also a one-time USGS catalog review. No site seismometers.",
   "location": "Public USGS network",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "Response plan lists shutting in injectors near a seismic event.",
   "pages": [
    22,
    23,
    29
   ],
   "evidence_quote": "CapturePoint monitors the USGS earthquake monitoring Geological Information System site3 for seismic signals"
  },
  {
   "method": "active_seismic",
   "commitment": "mentioned_only",
   "detail": "Past seismic evaluation cited as ruling out faults; no repeat seismic.",
   "location": "",
   "frequency": "one_time",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [
    22
   ],
   "evidence_quote": "Seismic evaluation has eliminated the existence of faults."
  },
  {
   "method": "surface_deformation",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "atmospheric_co2",
   "commitment": "not_found",
   "detail": "",
   "location": "",
   "frequency": "unspecified",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [],
   "evidence_quote": ""
  },
  {
   "method": "other",
   "commitment": "committed",
   "detail": "Subpart W emission factors and engineering estimates used to quantify surface equipment leaks and vents; emergency vent volume metered.",
   "location": "Surface equipment",
   "frequency": "annual",
   "baseline": "not_applicable",
   "trigger_or_response": "",
   "pages": [
    24,
    27,
    30,
    32,
    33
   ],
   "evidence_quote": "CapturePoint uses 40 CFR Part 98 Subpart W to estimate surface leaks from equipment at the WF."
  }
 ],
 "notes": "The plan says reservoir pressure is 'continuously monitored' but names no observation wells or gauges; it may mean pressures measured at injector headers (p28)."
}
