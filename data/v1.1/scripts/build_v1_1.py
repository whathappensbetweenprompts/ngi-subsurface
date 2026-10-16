# Gale, 2026-10-16: v1.1 - add RRC well-map layer (surface locations, well symbol) to site_wells.csv. Public data only.
import zipfile, io, glob, os, csv, collections, json
import shapefile, pandas as pd
SYM = {2:"Permitted Location",3:"Dry Hole",4:"Oil Well",5:"Gas Well",6:"Oil/Gas Well",7:"Plugged Oil Well",8:"Plugged Gas Well",
 9:"Canceled Location",10:"Plugged Oil/Gas Well",11:"Injection/Disposal Well",12:"Core Test",16:"Sulfur Core Test",17:"Storage from Oil",
 18:"Storage from Gas",19:"Shut-In Well (Oil)",20:"Shut-In Well (Gas)",21:"Injection/Disposal from Oil",22:"Injection/Disposal from Gas",
 23:"Injection/Disposal from Oil/Gas",36:"Geothermal Well",73:"Brine Mining Well",74:"Water Supply Well",75:"Water Supply from Oil",
 76:"Water Supply from Gas",77:"Water Supply from Oil/Gas",78:"Observation Well",79:"Observation from Oil",80:"Observation from Gas",
 81:"Observation from Oil/Gas",86:"Horizontal Well Surface Location",87:"Directional/Sidetrack Well Surface Location",88:"Storage Well",
 89:"Service Well",90:"Service from Oil",91:"Service from Gas",92:"Service from Oil/Gas",103:"Storage from Oil/Gas"}
REL = {"10":"Historic map (non-RRC)","15":"RRC hardcopy map","16":"Spotted from code-15 wells","17":"Adjusted during survey maintenance",
 "20":"Wellbore distances","25":"Plat/form without full data","30":"Operator reported (partial)","40":"Operator reported (distances and plat)",
 "45":"RRC field inspection","48":"Spotted from code-50 wells","50":"USGS quad or aerial imagery","55":"Coordinates from operator","60":"Coordinates reported by RRC personnel"}
surf = collections.defaultdict(list); bott = collections.defaultdict(list); unknown = collections.Counter()
for zf in sorted(glob.glob("raw/rrc/wells/well*.zip")):
    z = zipfile.ZipFile(zf); c = os.path.basename(zf)[4:7]
    for lay, store in (("s", surf), ("b", bott)):
        stem = f"well{c}{lay}"
        r = shapefile.Reader(shp=io.BytesIO(z.read(stem + ".shp")), dbf=io.BytesIO(z.read(stem + ".dbf")), shx=io.BytesIO(z.read(stem + ".shx")))
        names = [f[0] for f in r.fields[1:]]
        for rec in r.records():
            d = dict(zip(names, rec))
            api = (d.get("API") or "").strip()
            if len(api) == 8: store[api].append(d)
s = pd.read_csv("out/site_wells.csv", dtype=str, keep_default_na=False)
cols = {k: [] for k in ["rrc_map_found","rrc_map_symbol","rrc_map_symbol_code","surface_lat_nad83","surface_lon_nad83",
                        "location_reliability","location_reliability_code","rrc_map_surface_points","rrc_map_bottom_points"]}
for api10 in s.api10:
    a8 = api10[2:]
    pts = surf.get(a8, []); bp = bott.get(a8, [])
    if pts:
        # prefer the point with the best (highest) reliability code, then the most informative symbol
        p = sorted(pts, key=lambda d: (str(d.get("RELIAB") or ""), d.get("SYMNUM") or 0))[-1]
        code = int(p.get("SYMNUM") or 0); rel = str(p.get("RELIAB") or "").strip()
        if code not in SYM: unknown[code] += 1
        cols["rrc_map_found"].append("yes"); cols["rrc_map_symbol"].append(SYM.get(code, f"code {code}")); cols["rrc_map_symbol_code"].append(code)
        cols["surface_lat_nad83"].append(round(float(p["LAT83"]), 6)); cols["surface_lon_nad83"].append(round(float(p["LONG83"]), 6))
        cols["location_reliability"].append(REL.get(rel, rel)); cols["location_reliability_code"].append(rel)
    else:
        for k in ["rrc_map_symbol","rrc_map_symbol_code","surface_lat_nad83","surface_lon_nad83","location_reliability","location_reliability_code"]: cols[k].append("")
        cols["rrc_map_found"].append("yes_bottom_only" if bp else "no")
    cols["rrc_map_surface_points"].append(len(pts)); cols["rrc_map_bottom_points"].append(len(bp))
for k, v in cols.items(): s[k] = v
s["any_rrc_record"] = ((s.rrc_match == "matched") | (s.rrc_map_found != "no")).map({True: "yes", False: "no"})
s.to_csv("out/site_wells_v1_1.csv", index=False)
L = s[s.plan_role != "reference_in_text_figure_or_other_table"]
print("listed", len(L), "EWA matched", (L.rrc_match == "matched").sum(), "map found", (L.rrc_map_found != "no").sum(),
      "any", (L.any_rrc_record == "yes").sum(), "neither", (L.any_rrc_record == "no").sum())
U = L[L.rrc_match != "matched"]
print("of EWA-unmatched", len(U), ": on map", (U.rrc_map_found != "no").sum())
print(U[U.rrc_map_found != "no"].rrc_map_symbol.value_counts().to_string())
print("unknown symbol codes", dict(unknown))
print(L[L.any_rrc_record == "no"].groupby(["site_slug", "rrc_match"]).size().to_string())
