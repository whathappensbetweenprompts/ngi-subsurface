# Gale, 2026-10-16: v1.1 site summary + GeoJSON of listed wells with RRC map locations.
import json, pandas as pd
s = pd.read_csv("out/site_wells_v1_1.csv", dtype=str, keep_default_na=False)
sites = pd.read_csv("out/sites.csv", dtype=str, keep_default_na=False)
REF = "reference_in_text_figure_or_other_table"
add = []
for slug in sites.site_slug:
    L = s[(s.site_slug == slug) & (s.plan_role != REF)]
    U = L[L.rrc_match != "matched"]
    add.append({"site_slug": slug,
        "listed_on_rrc_map": int((L.rrc_map_found != "no").sum()),
        "listed_with_location": int((L.surface_lat_nad83 != "").sum()),
        "listed_not_in_ewa_but_on_map": int((U.rrc_map_found != "no").sum()),
        "listed_not_in_ewa_recent_or_permitted": int(U.rrc_map_symbol.isin(["Horizontal Well Surface Location", "Permitted Location", "Directional/Sidetrack Well Surface Location"]).sum()),
        "listed_no_rrc_digital_record": int((L.any_rrc_record == "no").sum())})
out = sites.merge(pd.DataFrame(add), on="site_slug")
out.to_csv("out/sites_v1_1.csv", index=False)
print(out[["site_slug","apis_listed_in_well_lists","listed_matched_rrc_ewa","listed_on_rrc_map","listed_not_in_ewa_recent_or_permitted","listed_no_rrc_digital_record"]].to_string())
feats = []
for _, r in s[(s.plan_role != REF) & (s.surface_lat_nad83 != "")].iterrows():
    feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(r.surface_lon_nad83), float(r.surface_lat_nad83)]},
        "properties": {k: r[k] for k in ["site_slug","api10","plan_role","plan_type_raw","plan_status_raw","rrc_match","rrc_map_symbol",
                                          "rrc_plug_date","rrc_depth_ft","location_reliability"]}})
json.dump({"type": "FeatureCollection", "name": "permian_storage_site_wells_v1_1",
           "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4269"}}, "features": feats},
          open("out/site_wells_v1_1.geojson", "w"), separators=(",", ":"))
print("features", len(feats))
