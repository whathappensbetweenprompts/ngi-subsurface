# Gale, 2026-10-16: one row per in-scope site: identity, source document, what kind of well list the plan carries, join results.
import json, csv
import pandas as pd
scope = json.load(open("work/scope.json"))
src = {r["site_slug"]: r for r in csv.DictReader(open("out/sources_epa_mrv_plans.csv", encoding="utf-8"))}
roles = json.load(open("work/table_roles.json"))
sw = pd.read_csv("out/site_wells.csv", dtype=str).fillna("")
dec = {"brown-pelican-co2-sequestration-project":"2025-08-22","denver-unit":"2023-08-21","seminole-san-andres-unit":"2023-08-21",
 "west-seminole-san-andres-unit":"2021-01-12","seminole-east-field-sef":"2022-10-20","south-plains-complex":"2025-07-09",
 "denver-city-fields":"2024-10-15","wellman":"2024-07-08","30-30-gas-plant":"2022-11-04","campo-viejo-gas-processing-plant":"2026-04-28",
 "targa-permian-co2-sequestration-well":"2025-07-16","milestone-carbon-delaware-ccs-hub":"2025-07-14","wildcat-gas-plant":"2025-01-08",
 "bull-moose-gas-plant":"2025-04-09","mongoose-amine-treating-facility":"2024-09-25","kinder-morgan-ccs-complex":"2023-07-20"}
rows = []
for s in scope:
    slug = s["site_slug"]; g = sw[sw.site_slug == slug]
    listed = g[g.plan_role != "reference_in_text_figure_or_other_table"]
    m = g[g.rrc_match == "matched"]
    rr = [r for r in roles if r[0] == slug]
    rows.append({"site_slug": slug, "site_name": s["site_name"], "operator_per_epa": s["operator"], "uic_class": s["uic_class"],
        "epa_decision_date": dec[slug], "counties_from_rrc_matches": ", ".join(f"{k} ({v})" for k, v in m.rrc_county.value_counts().items()),
        "plan_well_list_type": "; ".join(sorted(set(r[3] for r in rr))) or "none (wells discussed in text/figures without a numbered API list)",
        "plan_well_list_titles": " | ".join(f"p{r[1]}-{r[2]}: {r[4]}" for r in rr),
        "apis_listed_in_well_lists": len(listed), "apis_mentioned_elsewhere": len(g) - len(listed),
        "listed_matched_rrc_ewa": int((listed.rrc_match == "matched").sum()),
        "listed_unmatched": int((listed.rrc_match != "matched").sum()),
        "listed_with_rrc_plug_date": int((listed.rrc_plug_date != "").sum()),
        "plan_url": src[slug]["plan_url"], "epa_page": src[slug]["epa_page"], "plan_sha256": src[slug]["sha256"],
        "plan_retrieved_utc": src[slug]["retrieved_utc"]})
pd.DataFrame(rows).to_csv("out/sites.csv", index=False)
print(pd.DataFrame(rows)[["site_slug","plan_well_list_type","apis_listed_in_well_lists","listed_matched_rrc_ewa","listed_unmatched","listed_with_rrc_plug_date"]].to_string())

# mark scope in the plan source list
srcrows = list(csv.DictReader(open("out/sources_epa_mrv_plans.csv", encoding="utf-8")))
insc = {s["site_slug"] for s in scope}
for r in srcrows: r["in_scope"] = "yes" if r["site_slug"] in insc else "no"
with open("out/sources_epa_mrv_plans.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=[k for k in srcrows[0].keys()]); w.writeheader(); w.writerows(srcrows)
