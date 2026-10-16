# Coding guide: monitoring commitments in Subpart RR MRV plans (dataset v1.3)

You are reading EPA Subpart RR monitoring, reporting and verification (MRV) plans and recording, in a fixed structure, what each operator says it will monitor. Accuracy and page citations matter more than speed. Record only what the plan says; do not infer what the operator "probably" does.

## Inputs
- Plan text, one file per site: `/mnt/user-data/uploads/publish/_text_tmp/<site_slug>.txt`. Pages are delimited by lines `=====PAGE n=====`; `n` is the 1-based PDF page. Cite pages by this `n`, not by the page number printed in the document.
- Some pages are images with no text (they appear empty). If a section you need appears to be missing for that reason, say so in `notes`.
- Most plans follow the same outline. The sections that matter are usually: delineation of monitoring area and timeframes (AMA/MMA), evaluation of potential leakage pathways, the leakage detection/verification/quantification section (often with a risk/response table), monitoring for the mass balance (metering, composition), the "strategy for establishing expected baselines" or "determination of baselines", the implementation schedule, QA, and any appendix describing a monitoring program. Class VI plans (Brown Pelican) may also describe testing-and-monitoring plans with specific instruments and frequencies. Read all of these; skim the geology.

## Output
Write ONE JSON file per site to `/home/claude/NGI_contribution/v1_3/sites/<site_slug>.json` with this shape:

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
See `/home/claude/NGI_contribution/v1_3/sites/wellman.json`, which Gale coded. Match its style.

## Rules
- Copy quotes exactly (fixing only line-break hyphenation). Keep them under 25 words.
- `detail` and other free text: your own words, plain American English.
- `multi_year` means a stated interval longer than a year (e.g. MIT every five years); put the interval in `detail`.
- Don't invent frequencies. If the plan says "routine" without a number, use `periodic_unspecified`.
- Personal H2S monitors are not fixed detectors; visual inspection is not soil gas.
- Validate your JSON before finishing (python3 -c "import json; json.load(open(path))").
