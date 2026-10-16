"""Gale, 2026-10-16. Dataset v1.4: combine the Permian codings (v1.3, 23 sites) and the national codings (v1.4, 30 sites) into one national table."""
import csv, json, collections
P = "../v1.3/"; N = "out/"
nat_src = {r["site_slug"]: r for r in json.load(open("sources_national.json"))}
tx = {"brown-pelican-co2-sequestration-project","denver-unit","seminole-san-andres-unit","west-seminole-san-andres-unit","seminole-east-field-sef","south-plains-complex","denver-city-fields","wellman","30-30-gas-plant","campo-viejo-gas-processing-plant","targa-permian-co2-sequestration-well","milestone-carbon-delaware-ccs-hub","wildcat-gas-plant","bull-moose-gas-plant","mongoose-amine-treating-facility","kinder-morgan-ccs-complex"}
def meta(slug):
    if slug in nat_src: return nat_src[slug]["state"], "outside_permian", "api_batch_fable_5_1" if not slug.startswith("archer") else "hand_coded_in_session"
    return ("Texas" if slug in tx else "New Mexico"), "permian", "parallel_readers_in_session" if slug != "wellman" else "gale_worked_example"
GROUP = {"eor": "eor", "acid_gas_disposal": "class_ii_disposal", "co2_disposal": "class_ii_disposal", "class_vi_storage": "class_vi_storage"}
rows, sites = [], []
for src in (P, N):
    for r in csv.DictReader(open(src + "monitoring_commitments.csv", encoding="utf-8")): rows.append(r)
    for s in csv.DictReader(open(src + "monitoring_sites.csv", encoding="utf-8")):
        st, reg, how = meta(s["site_slug"]); s = {"site_slug": s["site_slug"], "state": st, "region": reg, "coded_by": how, "site_group": GROUP.get(s["injection_purpose"], s["injection_purpose"]), **{k: v for k, v in s.items() if k != "site_slug"}}
        sites.append(s)
with open("out/national_monitoring_commitments.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open("out/national_monitoring_sites.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(sites[0])); w.writeheader(); w.writerows(sites)
S = {s["site_slug"]: s for s in sites}; L = lambda slug, m: next(r for r in rows if r["site_slug"] == slug and r["method"] == m)["commitment"]
print("sites", len(sites), collections.Counter(s["site_group"] for s in sites), collections.Counter(s["region"] for s in sites))
for g in ["eor", "class_ii_disposal", "class_vi_storage"]:
    ss = [s for s in S if S[s]["site_group"] == g]
    print(f"\n{g} n={len(ss)}")
    for m in ["reservoir_pressure", "fixed_gas_detectors", "soil_gas", "groundwater_sampling", "atmospheric_co2", "above_zone_monitoring", "cased_hole_logging", "active_seismic", "surface_deformation"]:
        print(f"   {m:24s} committed {sum(L(s, m) == 'committed' for s in ss):2d}")
    print("   seismic source", dict(collections.Counter(S[s]["passive_seismic_source"] for s in ss)))
    print("   env baseline", sum(1 for s in ss if S[s]["committed_with_environmental_baseline"]))
