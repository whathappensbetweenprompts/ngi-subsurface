"""Gale, 2026-10-16. Dataset v1.3: assemble the per-site monitoring codings into tables and check every quote.

Inputs: sites/<slug>.json (one per site, coded per CODING_GUIDE.md) and the plan text files (=====PAGE n===== delimited).
Outputs (out/):
  monitoring_commitments.csv   one row per site x method
  monitoring_sites.csv         one row per site: plan facts, summaries, counts by commitment level, observation-network flags
  quote_check.csv              every non-empty evidence_quote, whether it was found on its cited pages
Usage: python3 build_v1_3.py <plan_text_dir>
"""
import csv, json, re, sys, os, glob, collections, unicodedata

TEXT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/publish/_text_tmp"
METHODS = ["injection_metering", "injection_pressure_scada", "annulus_pressure", "mechanical_integrity_testing", "production_monitoring",
           "reservoir_pressure", "visual_inspection", "personal_gas_monitors", "fixed_gas_detectors", "soil_gas", "groundwater_sampling",
           "above_zone_monitoring", "cased_hole_logging", "passive_seismic", "active_seismic", "surface_deformation", "atmospheric_co2", "other"]
LEVELS = ["committed", "conditional", "mentioned_only", "not_found"]
FREQ = {"continuous", "daily", "weekly", "monthly", "bimonthly", "quarterly", "semiannual", "annual", "multi_year", "periodic_unspecified", "event_driven", "one_time", "unspecified"}
BASE = {"yes", "no", "unclear", "not_applicable"}
os.makedirs("out", exist_ok=True)

def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    s = re.sub(r"-\s*\n\s*", "", s)          # line-break hyphenation
    s = re.sub(r"[^A-Za-z0-9%\.,;:'\"()/&+<>=\-§]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()

def compact(s):
    """Letters and digits only: tolerant of line breaks, real hyphens split across lines, and spacing."""
    return re.sub(r"[^a-z0-9]", "", norm(s))

def pages(slug):
    t = open(os.path.join(TEXT, slug + ".txt"), encoding="utf-8").read()
    return {int(p.split("=====")[0]): p.split("=====\n", 1)[1] for p in t.split("=====PAGE ")[1:]}

# Passive seismic source, read from each site's passive_seismic row by Gale (the coding vocabulary has one row for both cases)
SEISMIC_SOURCE = {
    "own_station": ["30-30-gas-plant", "brown-pelican-co2-sequestration-project", "bull-moose-gas-plant", "campo-viejo-gas-processing-plant",
                    "copperhead-gas-plant", "dark-horse-treating-plant", "milestone-carbon-delaware-ccs-hub", "red-hills-gas-processing-plant",
                    "targa-permian-co2-sequestration-well", "wildcat-gas-plant"],
    "public_network_only": ["denver-city-fields", "denver-unit", "dkl-libby-gas-plant", "kinder-morgan-ccs-complex", "maljamar-gas-plant",
                            "mongoose-amine-treating-facility", "seminole-east-field-sef", "seminole-san-andres-unit", "south-plains-complex",
                            "titan-treating-facility", "wellman", "west-seminole-san-andres-unit"],
    "none": ["hobbs-field"]}
SEIS = {s: k for k, v in SEISMIC_SOURCE.items() for s in v}
rows, sites, qc, problems = [], [], [], []
for f in sorted(glob.glob("sites/*.json")):
    d = json.load(open(f, encoding="utf-8")); slug = d["site_slug"]; P = pages(slug)
    seen = [r["method"] for r in d["rows"] if r["method"] != "other"]
    missing = [m for m in METHODS[:-1] if m not in seen]
    if missing: problems.append(f"{slug}: missing methods {missing}")
    dup = [m for m, c in collections.Counter(seen).items() if c > 1]
    if dup: problems.append(f"{slug}: duplicate methods {dup}")
    for r in d["rows"]:
        if r["method"] not in METHODS: problems.append(f"{slug}: bad method {r['method']}")
        if r["commitment"] not in LEVELS: problems.append(f"{slug}/{r['method']}: bad commitment {r['commitment']}")
        if r.get("frequency") not in FREQ: problems.append(f"{slug}/{r['method']}: bad frequency {r.get('frequency')}")
        if r.get("baseline") not in BASE: problems.append(f"{slug}/{r['method']}: bad baseline {r.get('baseline')}")
        if r["commitment"] != "not_found" and not r.get("pages"): problems.append(f"{slug}/{r['method']}: no pages")
        q = r.get("evidence_quote", "")
        if q:
            nq = compact(q); found_on = [p for p in r.get("pages", []) if p in P and nq in compact(P[p])]
            anywhere = found_on or [p for p in P if nq in compact(P[p])]
            # allow a quote that spans a page break between two cited pages
            if not found_on:
                cited = sorted(p for p in r.get("pages", []) if p in P)
                for a, b in zip(cited, cited[1:]):
                    if b == a + 1 and nq in compact(P[a] + " " + P[b]): found_on = [a, b]
            status = "on_cited_page" if found_on else ("elsewhere_in_plan" if anywhere else "not_found_in_text")
            qc.append({"site_slug": slug, "method": r["method"], "status": status, "cited_pages": ";".join(map(str, r.get("pages", []))),
                       "found_pages": ";".join(map(str, found_on or anywhere)), "quote": q, "words": len(q.split())})
        rows.append({"site_slug": slug, "method": r["method"], "commitment": r["commitment"], "detail": r.get("detail", ""), "location": r.get("location", ""),
                     "frequency": r.get("frequency", ""), "baseline": r.get("baseline", ""), "trigger_or_response": r.get("trigger_or_response", ""),
                     "pages": ";".join(map(str, r.get("pages", []))), "evidence_quote": q})
    by = {r["method"]: r for r in d["rows"] if r["method"] != "other"}
    lvl = lambda m: by.get(m, {}).get("commitment", "not_found")
    c = collections.Counter(r["commitment"] for r in d["rows"] if r["method"] != "other")
    near_surface = [m for m in ("soil_gas", "groundwater_sampling", "atmospheric_co2", "fixed_gas_detectors") if lvl(m) == "committed"]
    subsurface = [m for m in ("reservoir_pressure", "above_zone_monitoring", "cased_hole_logging") if lvl(m) == "committed"]
    geophys = [m for m in ("passive_seismic", "active_seismic", "surface_deformation") if lvl(m) == "committed"]
    env_baseline = [m for m in ("soil_gas", "groundwater_sampling", "atmospheric_co2", "surface_deformation", "passive_seismic")
                    if by.get(m, {}).get("baseline") == "yes" and lvl(m) == "committed"]
    sites.append({"site_slug": slug, "plan_title": d.get("plan_title", ""), "plan_version_or_date": d.get("plan_version_or_date", ""),
                  "injection_purpose": d.get("injection_purpose", ""), "uic_class_per_plan": d.get("uic_class_per_plan", ""),
                  "ama_definition": d.get("ama_definition", ""), "mma_definition": d.get("mma_definition", ""),
                  "leakage_pathways_rated_significant": d.get("leakage_pathways_rated_significant", ""),
                  "baseline_summary": d.get("baseline_summary", ""), "reporting_summary": d.get("reporting_summary", ""),
                  "n_committed": c["committed"], "n_conditional": c["conditional"], "n_mentioned_only": c["mentioned_only"], "n_not_found": c["not_found"],
                  "committed_near_surface_methods": ";".join(near_surface), "committed_subsurface_methods": ";".join(subsurface),
                  "committed_geophysical_methods": ";".join(geophys), "passive_seismic_source": SEIS.get(slug, "unclassified"), "committed_with_environmental_baseline": ";".join(env_baseline),
                  "notes": d.get("notes", "")})

with open("out/monitoring_commitments.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open("out/monitoring_sites.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(sites[0])); w.writeheader(); w.writerows(sites)
with open("out/quote_check.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(qc[0])); w.writeheader(); w.writerows(qc)
print("sites", len(sites), "rows", len(rows), "quotes", len(qc), collections.Counter(q["status"] for q in qc), "over25", sum(q["words"] > 25 for q in qc))
for p in problems: print("PROBLEM", p)
for q in qc:
    if q["status"] != "on_cited_page": print("QUOTE", q["status"], q["site_slug"], q["method"], q["cited_pages"], q["found_pages"], q["quote"][:90])
