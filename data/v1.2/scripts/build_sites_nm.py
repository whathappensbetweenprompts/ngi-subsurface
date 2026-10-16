# Gale, 2026-10-16. v1.2 site table and GeoJSON for the New Mexico wells; drops NMOCD columns the source leaves empty.
import csv, json, collections
R = list(csv.DictReader(open("out_nm/site_wells_nm.csv", encoding="utf-8")))
empty = [c for c in R[0] if not any(r[c] for r in R)]
print("empty columns dropped:", empty)
cols = [c for c in R[0] if c not in empty]
STATUS = {"Acti": "Active", "Plug": "Plugged", "New": "New (permitted, not drilled or not yet reported)", "Canc": "Cancelled", "Temp": "Temporarily abandoned", "Recl": "Recl"}
for r in R: r["nmocd_well_type"] = r.pop("nmocd_type_code", "")
cols = [("nmocd_well_type" if c == "nmocd_type_code" else c) for c in cols]
for r in R: r["nmocd_pre_ongard"] = "yes" if "PRE-ONGARD" in r["nmocd_well_name"] else ("" if r["nmocd_match"] != "matched" else "no")
cols.insert(cols.index("nmocd_operator") + 1, "nmocd_pre_ongard")
with open("out_nm/site_wells_nm_v1_2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(R)
src = {r["site_slug"]: r for r in csv.DictReader(open("out_nm/sources_epa_mrv_plans_nm.csv", encoding="utf-8"))}
roles = json.load(open("work_nm/table_roles_nm.json")); roles.pop("_note")
NAMES = {"hobbs-field": ("Hobbs Field", "Oxy"), "red-hills-gas-processing-plant": ("Red Hills Gas Processing Plant", "Targa Northern Delaware, LLC"),
         "maljamar-gas-plant": ("Maljamar Gas Plant", "Frontier Field Services, LLC"), "dark-horse-treating-plant": ("Dark Horse Treating Plant", "Pinon Midstream, LLC"),
         "titan-treating-facility": ("Titan Treating Facility", "Northwind Midstream Partners LLC"), "copperhead-gas-plant": ("Copperhead Gas Plant", "Targa Midstream Services, LLC"),
         "dkl-libby-gas-plant": ("DKL Libby Gas Plant", "DKL Delaware Operating - NM, LLC")}
S = []
for slug in src:
    l = [r for r in R if r["site_slug"] == slug and r["plan_role"] != "reference_in_text_figure_or_other_table"]
    lw = [r for r in l if r["plan_role"] != "project_wells"]
    S.append({"site_slug": slug, "site_name": NAMES[slug][0], "operator_per_plan": NAMES[slug][1],
              "plan_well_list_roles": ";".join(sorted({x[2] for x in roles[slug]})),
              "plan_well_list_titles": " | ".join(f"pp{x[0]}-{x[1]} ({x[3]}): {x[4]}" for x in roles[slug]),
              "apis_listed": len(l), "apis_listed_excluding_project_wells": len(lw),
              "apis_mentioned_elsewhere": sum(1 for r in R if r["site_slug"] == slug and r["plan_role"] == "reference_in_text_figure_or_other_table"),
              "listed_matched_nmocd": sum(r["nmocd_match"] == "matched" for r in l),
              "listed_nmocd_active": sum(r["nmocd_status"] == "Acti" for r in l), "listed_nmocd_plugged": sum(r["nmocd_status"] == "Plug" for r in l),
              "listed_nmocd_new": sum(r["nmocd_status"] == "New" for r in l), "listed_nmocd_other_status": sum(r["nmocd_match"] == "matched" and r["nmocd_status"] in ("Canc", "Temp", "Recl", "") for r in l),
              "listed_pre_ongard": sum(r["nmocd_pre_ongard"] == "yes" for r in l),
              "listed_horizontal": sum(r["nmocd_direction"] == "H" for r in l),
              "listed_ocr": sum("ocr" in r["plan_extraction"] for r in l),
              "plan_url": src[slug]["plan_url"], "epa_page": src[slug]["epa_page"], "plan_sha256": src[slug]["sha256"], "plan_retrieved_utc": src[slug]["retrieved_utc"]})
with open("out_nm/sites_nm_v1_2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(S[0])); w.writeheader(); w.writerows(S)
for s in S: print({k: v for k, v in s.items() if not k.startswith("plan_url") and k not in ("plan_sha256", "epa_page", "plan_retrieved_utc", "plan_well_list_titles")})
feats = []
for r in R:
    if r["plan_role"] == "reference_in_text_figure_or_other_table" or not r["lat_nad83"]: continue
    props = {k: r[k] for k in ("site_slug", "api10", "plan_role", "nmocd_well_name", "nmocd_operator", "nmocd_status", "nmocd_well_type", "nmocd_direction", "nmocd_pre_ongard", "nmslo_spud_date", "nmslo_plug_date", "plan_extraction")}
    feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(r["lon_nad83"]), float(r["lat_nad83"])]}, "properties": props})
json.dump({"type": "FeatureCollection", "features": feats}, open("out_nm/site_wells_nm_v1_2.geojson", "w"))
L = [r for r in R if r["plan_role"] != "reference_in_text_figure_or_other_table"]
print("features", len(feats), "listed", len(L), "unique", len({r["api10"] for r in L}), "shared across sites", sum(v > 1 for v in collections.Counter(r["api10"] for r in L).values()))
print("totals status", collections.Counter(r["nmocd_status"] for r in L), "pre-ongard", sum(r["nmocd_pre_ongard"] == "yes" for r in L), "pre-ongard spud", sum(bool(r["nmslo_spud_date"]) for r in L if r["nmocd_pre_ongard"] == "yes"), "pre-ongard plug", sum(bool(r["nmslo_plug_date"]) for r in L if r["nmocd_pre_ongard"] == "yes"))
print("plugged with plug date (either source)", sum(1 for r in L if r["nmocd_status"] == "Plug" and (r["nmocd_plug_date"] or r["nmslo_plug_date"])), "of", sum(r["nmocd_status"] == "Plug" for r in L))
print("excluding project wells", len([r for r in L if r["plan_role"] != "project_wells"]))
print("Hobbs listed status vs plan", collections.Counter((("P & A" in r["plan_row_raw"].split("3002")[-1][:40]) if r["site_slug"] == "hobbs-field" else None, r["nmocd_status"]) for r in L if r["site_slug"] == "hobbs-field"))
